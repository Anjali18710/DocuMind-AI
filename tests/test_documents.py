"""Metadata extraction, ingestion/OCR and revision-aware storage."""

import pytest

from conftest import SAMPLES, SEED
from rag.ingestion import IngestionError, build_chunks, ocr_available, read_pdf
from rag.metadata import extract_sop_metadata, match_heading, normalise_date
from rag.storage import ACTIVE, SUPERSEDED, add_pdf, delete_document, fingerprint

HEADER = """GAS_LEAK_EMERGENCY_SOP
STEEL AUTHORITY OF INDIA LIMITED
SOP No: BSP-GS-004
Title: Emergency Response Procedure for Gas Leak
Department: Safety and Environment
Revision: 03
Date: 20-Mar-2024
1. PURPOSE"""


# ── metadata ──────────────────────────────────────────────

def test_extracts_sop_header():
    meta = extract_sop_metadata(HEADER, "x.pdf")
    assert meta == {
        "sop_no": "BSP-GS-004",
        "title": "Emergency Response Procedure for Gas Leak",
        "department": "Safety and Environment",
        "revision": 3,
        "date": "20-Mar-2024",
    }


def test_missing_header_gets_defaults():
    meta = extract_sop_metadata("Some memo without a header", "boiler_notes.pdf")
    assert meta["sop_no"] is None and meta["revision"] == 0
    assert meta["title"] == "Boiler Notes" and meta["department"] == "General"


@pytest.mark.parametrize("line,expected", [
    ("5. IMMEDIATE RESPONSE PROCEDURE", ("5", "IMMEDIATE RESPONSE PROCEDURE")),
    ("4.2 Eye and Face Protection", ("4.2", "Eye and Face Protection")),
    ("- CO alarm (evacuate): 50 ppm", None),
    ("100 metres from the leak point", None),
])
def test_heading_detection(line, expected):
    assert match_heading(line) == expected


def test_date_normalisation():
    assert normalise_date("05/06/2024") == "05-Jun-2024"


# ── ingestion ─────────────────────────────────────────────

def test_chunks_carry_citation_metadata():
    data = (SEED / "GAS_LEAK_EMERGENCY_SOP.pdf").read_bytes()
    meta, pages, _ = read_pdf(data, "GAS_LEAK_EMERGENCY_SOP.pdf")
    meta["doc_id"] = "d1"
    chunks = build_chunks(pages, meta)
    thresholds = next(c for c in chunks if "50 ppm" in c.metadata["body"])
    assert thresholds.metadata["section"] == "4. DETECTION THRESHOLDS"
    assert thresholds.metadata["page"] == 1 and thresholds.metadata["revision"] == 3
    # title + section prepended for better search, raw text kept for display
    assert thresholds.page_content.startswith("Emergency Response Procedure for Gas Leak (BSP-GS-004)")


def test_rejects_non_pdf():
    with pytest.raises(IngestionError):
        read_pdf(b"not a pdf", "fake.pdf")


@pytest.mark.skipif(not ocr_available(), reason="Tesseract not installed")
def test_scanned_pdf_is_read_with_ocr():
    data = (SEED / "GAS_DETECTOR_CALIBRATION_SOP_SCANNED.pdf").read_bytes()
    meta, pages, ocr_pages = read_pdf(data, "scan.pdf")
    assert ocr_pages == 1
    assert meta["sop_no"] == "BSP-GS-006"
    assert "30 days" in pages[0]


# ── storage & revision rules ──────────────────────────────

def test_seeding_loads_all_bundled_sops(seeded_store):
    active = seeded_store.list_documents(ACTIVE)
    assert len(active) == len(list(SEED.glob("*.pdf")))
    assert "page_texts" not in active[0]  # heavy text only loaded on request


def test_duplicate_upload_rejected(seeded_store):
    data = (SEED / "GAS_LEAK_EMERGENCY_SOP.pdf").read_bytes()
    result = add_pdf(seeded_store, data, "copy.pdf")
    assert not result["ok"] and "identical" in result["message"]


def test_new_revision_supersedes_old_and_delete_rolls_back(seeded_store):
    before = fingerprint(seeded_store)
    rev4 = (SAMPLES / "GAS_LEAK_EMERGENCY_SOP_Rev04.pdf").read_bytes()
    result = add_pdf(seeded_store, rev4, "GAS_LEAK_EMERGENCY_SOP_Rev04.pdf")
    assert result["ok"] and "superseded" in result["message"]

    gas = [d for d in seeded_store.list_documents() if d["sop_no"] == "BSP-GS-004"]
    status = {d["revision"]: d["status"] for d in gas}
    assert status == {3: SUPERSEDED, 4: ACTIVE}
    assert fingerprint(seeded_store) != before  # index will rebuild

    # Uploading the old revision again is refused
    rev3 = (SEED / "GAS_LEAK_EMERGENCY_SOP.pdf").read_bytes()
    assert not add_pdf(seeded_store, rev3 + b"\n%changed", "old.pdf")["ok"]

    # Deleting Rev 04 makes Rev 03 active again
    message = delete_document(seeded_store, result["record"]["doc_id"])
    assert "active again" in message
    active = [d for d in seeded_store.list_documents(ACTIVE) if d["sop_no"] == "BSP-GS-004"]
    assert [d["revision"] for d in active] == [3]
    assert fingerprint(seeded_store) == before


def test_mongo_store_same_behaviour():
    mongomock = pytest.importorskip("mongomock")
    import mongomock.gridfs

    from rag.storage import MongoStore, seed_if_empty

    mongomock.gridfs.enable_gridfs_integration()
    store = MongoStore(client=mongomock.MongoClient(), db_name="test")
    seed_if_empty(store, str(SEED))
    doc = store.list_documents(ACTIVE)[0]
    assert store.get_pdf(doc["doc_id"]).startswith(b"%PDF")
    store.log_query({"query_id": "q1", "ts": "2026-01-01", "question": "hi", "feedback": None})
    store.update_query("q1", {"feedback": 1})
    assert store.list_queries()[0]["feedback"] == 1
