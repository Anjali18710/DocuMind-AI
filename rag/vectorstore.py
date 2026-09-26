"""
vectorstore.py
--------------
Builds the FAISS index from the chunks of all *active* documents.

The index is cached on disk together with a fingerprint of the active
document set and the embedding model. When a document is added, replaced
or deleted the fingerprint changes and the index is rebuilt; otherwise the
cached copy is loaded, which makes restarts fast.
"""

import os
import shutil
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document

from config.settings import EMBEDDING_MODEL, INDEX_CACHE_DIR
from rag.embeddings import get_embedding_model

_FINGERPRINT_FILE = "fingerprint.txt"


def build_vectorstore(chunks: List[Document]) -> FAISS:
    print(f"── Building vector store ({len(chunks)} chunks) ──")
    return FAISS.from_documents(
        chunks,
        get_embedding_model(),
        # Inner product on normalised vectors = cosine similarity.
        distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
    )


def _cache_key(fingerprint: str) -> str:
    return f"{fingerprint}|{EMBEDDING_MODEL}"


def load_cached(fingerprint: str, cache_dir: str = INDEX_CACHE_DIR):
    """Return the cached FAISS index if it matches the current documents, else None."""
    marker = os.path.join(cache_dir, _FINGERPRINT_FILE)
    if not os.path.exists(marker):
        return None
    with open(marker, encoding="utf-8") as f:
        if f.read().strip() != _cache_key(fingerprint):
            return None
    try:
        return FAISS.load_local(
            cache_dir,
            get_embedding_model(),
            # Safe here: we only ever load an index this app wrote itself.
            allow_dangerous_deserialization=True,
            distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
        )
    except Exception as exc:
        print(f"Cached index unreadable, rebuilding: {exc}")
        return None


def save_cache(vectorstore: FAISS, fingerprint: str, cache_dir: str = INDEX_CACHE_DIR):
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    vectorstore.save_local(cache_dir)
    with open(os.path.join(cache_dir, _FINGERPRINT_FILE), "w", encoding="utf-8") as f:
        f.write(_cache_key(fingerprint))


def all_chunks(vectorstore: FAISS) -> List[Document]:
    """Every chunk stored in the index, in index order (used to build BM25)."""
    return [
        vectorstore.docstore.search(doc_id)
        for _, doc_id in sorted(vectorstore.index_to_docstore_id.items())
    ]
