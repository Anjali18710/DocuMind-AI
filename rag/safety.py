"""
safety.py
---------
Guards for safety-critical answers.

1. `is_safety_critical` — spots emergency / PPE / hazard questions (English,
   Hindi and common Hinglish), so the app shows the SOP's exact wording
   instead of relying only on an AI paraphrase.
2. `find_unverified_numbers` — every number in the AI's answer must appear
   in the retrieved SOP text. A number that doesn't (e.g. "150 metres" when
   the SOP says 100) is flagged to the user as a possible error.
"""

import re
from typing import Iterable, List

_SAFETY_TERMS = [
    # English
    "emergency", "leak", "gas", "fire", "explosion", "evacuat", "ppe", "protective",
    "helmet", "hard hat", "goggle", "glove", "scba", "breathing apparatus", "respirator",
    "shutdown", "shut down", "isolation", "lockout", "loto", "tagout", "permit",
    "confined space", "height", "harness", "burn", "injur", "first aid", "unconscious",
    "rescue", "alarm", "toxic", "poison", "hazard", "danger", "carbon monoxide",
    "ppm", "breakout", "splash", "molten", "hot metal", "electric shock", "safe distance",
    "oxygen", "heat stroke", "heat stress",
    # Hindi (Devanagari)
    "आपात", "रिसाव", "गैस", "आग", "विस्फोट", "सुरक्षा", "खतरा", "जहरीली", "बचाव",
    "प्राथमिक चिकित्सा", "घायल", "बेहोश", "जलना", "जल गया", "दस्ताने", "हेलमेट",
    # Hinglish
    "suraksha", "khatra", "aag", "bachav", "chot",
]
_CO_RE = re.compile(r"\bco\b", re.IGNORECASE)


def is_safety_critical(question: str) -> bool:
    q = question.lower()
    return any(term in q for term in _SAFETY_TERMS) or bool(_CO_RE.search(question))


# ── Number verification ───────────────────────────────────

_DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*")
_CITATION_RE = re.compile(r"\[[^\]]*\]")
_LIST_MARKER_RE = re.compile(r"^\s*\d{1,2}[.)]\s+", re.MULTILINE)
_STEP_RE = re.compile(r"\b(?:step|चरण)\s*\d{1,2}\b", re.IGNORECASE)


def _numbers(text: str) -> List[str]:
    text = text.translate(_DEVANAGARI_DIGITS)
    found = []
    for raw in _NUMBER_RE.findall(text):
        raw = raw.rstrip(".,")
        found.append(_normalise(raw))
        # "1,000" and "1.5" also count as their parts in case the source
        # writes them differently ("1000", "1 . 5").
        found.extend(_normalise(p) for p in re.split(r"[.,]", raw) if p)
    return found


def _normalise(num: str) -> str:
    num = num.replace(",", "")
    if "." in num:
        num = num.rstrip("0").rstrip(".")
    return num.lstrip("0") or "0"


def find_unverified_numbers(answer: str, source_texts: Iterable[str]) -> List[str]:
    """
    Numbers in the answer that do not appear anywhere in the sources.
    Citations in [brackets], list numbering ("1.") and "Step 3" are ignored.
    """
    cleaned = _CITATION_RE.sub(" ", answer)
    cleaned = _LIST_MARKER_RE.sub(" ", cleaned)
    cleaned = _STEP_RE.sub(" ", cleaned)

    allowed = set()
    for text in source_texts:
        allowed.update(_numbers(text))

    unverified = []
    for raw in _NUMBER_RE.findall(cleaned.translate(_DEVANAGARI_DIGITS)):
        raw = raw.rstrip(".,")
        if _normalise(raw) not in allowed and raw not in unverified:
            unverified.append(raw)
    return unverified
