"""
metadata.py
-----------
Reads the SOP header block (SOP No, Title, Department, Revision, Date)
from the first page of a document, and detects section headings so every
chunk knows which section it came from.
"""

import re
from datetime import datetime
from typing import Optional

_FIELD_PATTERNS = {
    "sop_no": r"SOP\s*No\.?\s*[:\-]\s*([A-Z0-9][A-Z0-9\-/]+)",
    "title": r"Title\s*[:\-]\s*(.+)",
    "department": r"Department\s*[:\-]\s*(.+)",
    "revision": r"Rev(?:ision)?\.?\s*(?:No\.?)?\s*[:\-]\s*([0-9]+)",
    "date": r"(?:Effective\s+)?Date\s*[:\-]\s*([0-9]{1,2}[\-/ ][A-Za-z0-9]{2,9}[\-/ ][0-9]{2,4})",
}

# "5. SHUTDOWN PROCEDURE", "4.2 Eye and Face Protection", "10. REPORTING"
_HEADING_RE = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2})*)\.?\s+([A-Z][^\n]{2,90})$")


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" .:-")


def extract_sop_metadata(first_page_text: str, filename: str) -> dict:
    """Pull header fields out of the first page. Missing fields get safe defaults."""
    text = first_page_text.replace("\r", "")
    meta = {}
    for field, pattern in _FIELD_PATTERNS.items():
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        meta[field] = _clean(match.group(1)) if match else None

    stem = re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE)
    if not meta["title"]:
        meta["title"] = stem.replace("_", " ").title()
    if not meta["department"]:
        meta["department"] = "General"
    meta["sop_no"] = meta["sop_no"].upper() if meta["sop_no"] else None
    meta["revision"] = int(meta["revision"]) if meta["revision"] else 0
    meta["date"] = normalise_date(meta["date"]) if meta["date"] else None
    return meta


def normalise_date(raw: str) -> str:
    """Return dates as DD-Mon-YYYY where possible, otherwise unchanged."""
    raw = raw.strip()
    for fmt in ("%d-%b-%Y", "%d-%B-%Y", "%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%d-%b-%Y")
        except ValueError:
            continue
    return raw


def match_heading(line: str) -> Optional[tuple]:
    """If the line is a numbered section heading, return (number, heading text)."""
    line = line.strip()
    if len(line) > 95:
        return None
    match = _HEADING_RE.match(line)
    if not match:
        return None
    number, heading = match.group(1), match.group(2).strip()
    # Reject things like "2 Hard hats must be..." (sentences, not headings)
    if heading.endswith(".") and not heading.isupper():
        return None
    return number, heading


def format_revision(revision: int) -> str:
    return f"Rev {revision:02d}" if revision else "Rev —"
