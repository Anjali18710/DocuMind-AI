"""
ingestion.py
------------
Turns a PDF (as bytes) into searchable chunks.

1. Extract text page by page (pypdf). Pages with almost no text are
   treated as scanned images and read with OCR (Tesseract), if available.
2. Read the SOP header (SOP No, Revision, Department, ...) from page 1.
3. Split the text by numbered section, then into ~800-character chunks.
   Each chunk remembers its document, revision, page and section so the
   app can cite it precisely.
"""

import io
import logging
import re
from typing import List, Tuple

import pypdfium2 as pdfium
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, OCR_ENABLED, OCR_MIN_CHARS
from rag.metadata import extract_sop_metadata, match_heading

log = logging.getLogger(__name__)


# Repeated page furniture that should not end up in search results
_BOILERPLATE = [
    re.compile(r"^\s*illustrative sample sop created for the documind", re.IGNORECASE),
    re.compile(r"^\s*page\s+\d+(\s+of\s+\d+)?\s*$", re.IGNORECASE),
]


def _strip_boilerplate(text: str) -> str:
    return "\n".join(l for l in text.split("\n") if not any(p.search(l) for p in _BOILERPLATE))


class IngestionError(ValueError):
    """Raised when a PDF cannot be turned into usable text."""


# ── Text extraction ───────────────────────────────────────

def _ocr_page(page) -> str:
    """Render one PDF page to an image and read it with Tesseract."""
    try:
        import pytesseract
    except ImportError:
        return ""
    try:
        image = page.render(scale=300 / 72).to_pil()  # ~300 DPI
        return pytesseract.image_to_string(image)
    except Exception as exc:  # Tesseract binary missing, bad image, ...
        log.warning("OCR failed: %s", exc)
        return ""


def ocr_available() -> bool:
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_pages(pdf_bytes: bytes) -> Tuple[List[str], int]:
    """Return (text of each page, number of pages that needed OCR)."""
    # pypdf (v5+) keeps the line structure of SOPs best, so it reads the text
    # layer; pypdfium2 is used only to render scanned pages for OCR.
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        texts = [(page.extract_text() or "") for page in reader.pages]
    except Exception as exc:
        raise IngestionError(f"This file could not be opened as a PDF ({exc}).")

    pages, ocr_count = [], 0
    use_ocr = OCR_ENABLED and ocr_available()
    rendered = None
    for i, text in enumerate(texts):
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if len(text.strip()) < OCR_MIN_CHARS and use_ocr:
            rendered = rendered or pdfium.PdfDocument(io.BytesIO(pdf_bytes))
            ocr_text = _ocr_page(rendered[i])
            if len(ocr_text.strip()) > len(text.strip()):
                text, ocr_count = ocr_text, ocr_count + 1
        pages.append(_strip_boilerplate(text))
    if rendered is not None:
        rendered.close()
    return pages, ocr_count


# ── Chunking ──────────────────────────────────────────────

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def _sections(pages: List[str]):
    """
    Yield (page_number, section_label, text) blocks. A new block starts at
    every numbered heading or page break; the section label carries over
    across pages.
    """
    top, sub = "Header", None
    for page_no, page_text in enumerate(pages, start=1):
        buffer = []
        for line in page_text.split("\n"):
            heading = match_heading(line)
            if heading:
                if buffer:
                    yield page_no, _label(top, sub), "\n".join(buffer)
                    buffer = []
                number, text = heading
                if "." in number:
                    sub = f"{number} {text}"
                else:
                    top, sub = f"{number}. {text}", None
            buffer.append(line)
        if buffer:
            yield page_no, _label(top, sub), "\n".join(buffer)


def _label(top: str, sub) -> str:
    return f"{top} › {sub}" if sub else top


def build_chunks(pages: List[str], doc_meta: dict) -> List[Document]:
    """Split pages into chunks carrying full citation metadata."""
    chunks = []
    header = f"{doc_meta['title']} ({doc_meta.get('sop_no') or doc_meta['filename']})"
    for page_no, section, text in _sections(pages):
        if not text.strip():
            continue
        for part in _splitter.split_text(text):
            body = part.strip()
            if len(body) < 15 or ("\n" not in body and match_heading(body)):
                continue  # too small, or just a heading with nothing under it
            chunk_id = f"{doc_meta['doc_id']}:{page_no}:{len(chunks)}"
            chunks.append(
                Document(
                    # The document title + section are prepended so that a
                    # chunk like "- Minimum safe distance: 100 metres" still
                    # "knows" it belongs to the gas-leak SOP when searched.
                    page_content=f"{header} — {section}\n{body}",
                    metadata={
                        "chunk_id": chunk_id,
                        "doc_id": doc_meta["doc_id"],
                        "source": doc_meta["filename"],
                        "sop_no": doc_meta.get("sop_no"),
                        "title": doc_meta["title"],
                        "department": doc_meta["department"],
                        "revision": doc_meta["revision"],
                        "date": doc_meta.get("date"),
                        "page": page_no,
                        "section": section,
                        "body": body,
                    },
                )
            )
    return chunks


def read_pdf(pdf_bytes: bytes, filename: str) -> Tuple[dict, List[str], int]:
    """
    Extract text + header metadata from a PDF.
    Returns (metadata, pages, ocr_page_count). Raises IngestionError when
    no readable text can be found.
    """
    pages, ocr_count = extract_pages(pdf_bytes)
    if sum(len(p.strip()) for p in pages) < 50:
        hint = "" if ocr_available() else " OCR (Tesseract) is not installed on this machine."
        raise IngestionError(
            f"No readable text found in '{filename}'. It may be a scanned image.{hint}"
        )
    meta = extract_sop_metadata(pages[0], filename)
    meta["filename"] = filename
    meta["pages"] = len(pages)
    meta["ocr_pages"] = ocr_count
    return meta, pages, ocr_count
