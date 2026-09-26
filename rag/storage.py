"""
storage.py
----------
Where documents, their revision history and the usage logs live.

* MongoStore — MongoDB Atlas (PDFs in GridFS). Used when MONGODB_URI is set.
  Survives app restarts, which Streamlit Community Cloud's disk does not.
* LocalStore — a folder on disk (data/store/). Used for local development.

Both expose the same small interface; the revision rules (duplicates,
superseding older revisions, rollback on delete) are written once, in
`add_pdf` and `delete_document`, on top of that interface.
"""

import hashlib
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from config.settings import LOCAL_STORE_DIR, MONGODB_DB, MONGODB_URI, SEED_DIR
from rag.ingestion import IngestionError, read_pdf
from rag.metadata import format_revision

ACTIVE, SUPERSEDED = "active", "superseded"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── Store implementations ─────────────────────────────────

class LocalStore:
    kind = "Local folder"

    def __init__(self, root: str = LOCAL_STORE_DIR):
        self.root = Path(root)
        (self.root / "pdfs").mkdir(parents=True, exist_ok=True)
        self._docs_file = self.root / "documents.json"
        self._queries_file = self.root / "queries.json"
        self._lock = threading.Lock()

    def _read(self, path: Path) -> list:
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _write(self, path: Path, data: list):
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)

    # documents
    def list_documents(self, status: Optional[str] = None, include_text: bool = False) -> List[dict]:
        docs = self._read(self._docs_file)
        docs = [d for d in docs if status is None or d["status"] == status]
        if not include_text:
            docs = [{k: v for k, v in d.items() if k != "page_texts"} for d in docs]
        return docs

    def get_document(self, doc_id: str) -> Optional[dict]:
        return next((d for d in self.list_documents() if d["doc_id"] == doc_id), None)

    def get_pdf(self, doc_id: str) -> bytes:
        return (self.root / "pdfs" / f"{doc_id}.pdf").read_bytes()

    def insert_document(self, record: dict, pdf_bytes: bytes):
        with self._lock:
            (self.root / "pdfs" / f"{record['doc_id']}.pdf").write_bytes(pdf_bytes)
            docs = self._read(self._docs_file)
            docs.append(record)
            self._write(self._docs_file, docs)

    def update_document(self, doc_id: str, fields: dict):
        with self._lock:
            docs = self._read(self._docs_file)
            for d in docs:
                if d["doc_id"] == doc_id:
                    d.update(fields)
            self._write(self._docs_file, docs)

    def remove_document(self, doc_id: str):
        with self._lock:
            docs = [d for d in self._read(self._docs_file) if d["doc_id"] != doc_id]
            self._write(self._docs_file, docs)
            pdf = self.root / "pdfs" / f"{doc_id}.pdf"
            if pdf.exists():
                pdf.unlink()

    # query log
    def log_query(self, record: dict):
        with self._lock:
            queries = self._read(self._queries_file)
            queries.append(record)
            self._write(self._queries_file, queries[-5000:])

    def update_query(self, query_id: str, fields: dict):
        with self._lock:
            queries = self._read(self._queries_file)
            for q in queries:
                if q["query_id"] == query_id:
                    q.update(fields)
            self._write(self._queries_file, queries)

    def list_queries(self, limit: int = 2000) -> List[dict]:
        return list(reversed(self._read(self._queries_file)))[:limit]


class MongoStore:
    kind = "MongoDB Atlas"

    def __init__(self, uri: str = MONGODB_URI, db_name: str = MONGODB_DB, client=None):
        import gridfs
        from pymongo import MongoClient

        self.client = client or MongoClient(uri, serverSelectionTimeoutMS=8000)
        self.db = self.client[db_name]
        self.docs = self.db["documents"]
        self.queries = self.db["queries"]
        self.fs = gridfs.GridFS(self.db, collection="pdfs")
        self.docs.create_index("doc_id", unique=True)
        self.queries.create_index("query_id", unique=True)

    def list_documents(self, status: Optional[str] = None, include_text: bool = False) -> List[dict]:
        query = {"status": status} if status else {}
        projection = {"_id": 0} if include_text else {"_id": 0, "page_texts": 0}
        return list(self.docs.find(query, projection).sort("uploaded_at", 1))

    def get_document(self, doc_id: str) -> Optional[dict]:
        return self.docs.find_one({"doc_id": doc_id}, {"_id": 0, "page_texts": 0})

    def get_pdf(self, doc_id: str) -> bytes:
        return self.fs.find_one({"doc_id": doc_id}).read()

    def insert_document(self, record: dict, pdf_bytes: bytes):
        self.fs.put(pdf_bytes, filename=record["filename"], doc_id=record["doc_id"])
        self.docs.insert_one(dict(record))

    def update_document(self, doc_id: str, fields: dict):
        self.docs.update_one({"doc_id": doc_id}, {"$set": fields})

    def remove_document(self, doc_id: str):
        self.docs.delete_one({"doc_id": doc_id})
        for f in self.fs.find({"doc_id": doc_id}):
            self.fs.delete(f._id)

    def log_query(self, record: dict):
        self.queries.insert_one(dict(record))

    def update_query(self, query_id: str, fields: dict):
        self.queries.update_one({"query_id": query_id}, {"$set": fields})

    def list_queries(self, limit: int = 2000) -> List[dict]:
        return list(self.queries.find({}, {"_id": 0}).sort("ts", -1).limit(limit))


def get_store():
    """MongoDB if configured, otherwise the local folder."""
    if MONGODB_URI:
        return MongoStore()
    return LocalStore()


# ── Revision-aware document operations ────────────────────

def add_pdf(store, pdf_bytes: bytes, filename: str, uploaded_by: str = "admin") -> dict:
    """
    Add a PDF to the knowledge base, applying the revision rules:
      * exact same file already stored          → rejected (duplicate)
      * same SOP No, higher revision            → added; old one marked superseded
      * same SOP No, same or lower revision     → rejected
      * no SOP No and the filename already used → rejected
    Returns {"ok": bool, "message": str, "record": dict | None}.
    """
    sha = hashlib.sha256(pdf_bytes).hexdigest()
    existing = store.list_documents()

    dup = next((d for d in existing if d["sha256"] == sha), None)
    if dup:
        return _fail(f"'{filename}' is identical to '{dup['filename']}', which is already stored.")

    try:
        meta, pages, ocr_pages = read_pdf(pdf_bytes, filename)
    except IngestionError as exc:
        return _fail(str(exc))

    active = [d for d in existing if d["status"] == ACTIVE]
    previous = None
    if meta["sop_no"]:
        previous = next((d for d in active if d.get("sop_no") == meta["sop_no"]), None)
        if previous and meta["revision"] <= previous["revision"]:
            return _fail(
                f"{meta['sop_no']} {format_revision(previous['revision'])} is already active. "
                f"The uploaded file is {format_revision(meta['revision'])}, so it was not added. "
                "Upload a higher revision, or delete the current one first."
            )
    elif any(d["filename"] == filename for d in active):
        return _fail(f"A document named '{filename}' already exists. Delete it first or rename the file.")

    record = {
        **meta,
        "doc_id": uuid.uuid4().hex[:12],
        "sha256": sha,
        "status": ACTIVE,
        "superseded_by": None,
        "supersedes": previous["doc_id"] if previous else None,
        "uploaded_at": _now(),
        "uploaded_by": uploaded_by,
        "page_texts": pages,
    }
    store.insert_document(record, pdf_bytes)

    message = f"Added {meta.get('sop_no') or filename} ({format_revision(meta['revision'])})."
    if previous:
        store.update_document(
            previous["doc_id"],
            {"status": SUPERSEDED, "superseded_by": record["doc_id"], "superseded_at": _now()},
        )
        message += f" {format_revision(previous['revision'])} is now marked as superseded."
    if ocr_pages:
        message += f" {ocr_pages} scanned page(s) were read with OCR."
    return {"ok": True, "message": message, "record": record}


def delete_document(store, doc_id: str) -> str:
    """Delete a document. If it had replaced an older revision, that one becomes active again."""
    doc = store.get_document(doc_id)
    if not doc:
        return "Document not found."
    store.remove_document(doc_id)
    message = f"Deleted {doc.get('sop_no') or doc['filename']} ({format_revision(doc['revision'])})."
    if doc["status"] == ACTIVE and doc.get("supersedes"):
        older = store.get_document(doc["supersedes"])
        if older:
            store.update_document(older["doc_id"], {"status": ACTIVE, "superseded_by": None})
            message += f" {format_revision(older['revision'])} is active again."
    return message


def seed_if_empty(store, seed_dir: str = SEED_DIR) -> int:
    """First run: load the bundled SOPs from data/raw/ into the store."""
    if store.list_documents():
        return 0
    added = 0
    for pdf in sorted(Path(seed_dir).glob("*.pdf")):
        result = add_pdf(store, pdf.read_bytes(), pdf.name, uploaded_by="seed")
        added += int(result["ok"])
    return added


def fingerprint(store) -> str:
    """Changes whenever the set of active documents changes (used to rebuild the index)."""
    ids = sorted(d["doc_id"] for d in store.list_documents(ACTIVE))
    return hashlib.sha1("|".join(ids).encode()).hexdigest()[:16]


def _fail(message: str) -> dict:
    return {"ok": False, "message": message, "record": None}
