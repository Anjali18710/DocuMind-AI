"""
pipeline.py
-----------
One function, `answer_question`, that runs the whole flow for a question.
It has no Streamlit code, so the app and the evaluation script share it.

    question
      → hybrid search (FAISS + BM25)            retriever.py
      → confidence gate: weak match? say "not covered", skip the LLM
      → safety question? pull exact SOP text     safety.py
      → LLM answer with citations (auto fallback) chain.py
      → check every number against the sources  safety.py
"""

import re
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from config.settings import REFUSAL_CONTACT, TOP_K_RESULTS
from rag.chain import NOT_FOUND_TOKEN, LLMRouter, build_qa_prompt, citation
from rag.retriever import HybridRetriever
from rag.safety import find_unverified_numbers, is_safety_critical

_DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")

LANGUAGES = {"Auto": None, "English": "English", "हिन्दी (Hindi)": "Hindi"}


def resolve_language(choice: str, question: str) -> str:
    fixed = LANGUAGES.get(choice)
    if fixed:
        return fixed
    return "Hindi" if _DEVANAGARI_RE.search(question) else "English"


def refusal_message(language: str) -> str:
    if language == "Hindi":
        return f"यह जानकारी वर्तमान SOPs में उपलब्ध नहीं है। कृपया {REFUSAL_CONTACT} से संपर्क करें।"
    return f"This is not covered in the current SOPs. Please contact {REFUSAL_CONTACT}."


def _verbatim_blocks(chunks, max_blocks: int = 3):
    """Exact SOP text from the top-ranked document, in document order."""
    if not chunks:
        return []
    top_doc = chunks[0].metadata["doc_id"]
    same_doc = [c for c in chunks if c.metadata["doc_id"] == top_doc][:max_blocks]
    same_doc.sort(key=lambda c: (c.metadata["page"], int(c.metadata["chunk_id"].rsplit(":", 1)[1])))
    return [
        {"citation": citation(c.metadata), "title": c.metadata["title"], "text": c.metadata["body"]}
        for c in same_doc
    ]


def answer_question(
    question: str,
    retriever: HybridRetriever,
    llm: Optional[LLMRouter],
    department: Optional[str] = None,
    language_choice: str = "Auto",
    k: int = TOP_K_RESULTS,
    mode: str = "hybrid",
) -> dict:
    started = time.time()
    language = resolve_language(language_choice, question)
    safety = is_safety_critical(question)
    result = retriever.search(question, k=k, department=department, mode=mode)

    out = {
        "query_id": uuid.uuid4().hex[:12],
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "question": question,
        "language": language,
        "department_filter": department,
        "safety_critical": safety,
        "retrieval": {
            "best_similarity": round(result.best_similarity, 3),
            "best_bm25": round(result.best_bm25, 2),
            "confident": result.confident,
            "reranked": result.reranked,
        },
        "citations": [],
        "verbatim": [],
        "unverified_numbers": [],
        "model": None,
        "refused": False,
        "refusal_reason": None,
        "top_sop": result.chunks[0].metadata.get("sop_no") if result.chunks else None,
        "top_department": result.chunks[0].metadata.get("department") if result.chunks else None,
        "retrieved_sops": [c.metadata.get("sop_no") or c.metadata["source"] for c in result.chunks],
        "feedback": None,
    }

    if not result.confident:
        out.update(answer=refusal_message(language), refused=True, refusal_reason="low_match")
        out["latency_ms"] = int((time.time() - started) * 1000)
        return out

    if safety:
        out["verbatim"] = _verbatim_blocks(result.chunks)

    if llm is None:  # retrieval-only mode (used by the evaluation script)
        out["answer"] = ""
    else:
        prompt = build_qa_prompt(question, result.chunks, language, safety)
        text, model_used = llm.generate(prompt)
        out["model"] = model_used
        if text.strip().strip(".").upper().startswith(NOT_FOUND_TOKEN):
            out.update(answer=refusal_message(language), refused=True, refusal_reason="llm_not_found")
        else:
            out["answer"] = text
            sources = [c.metadata["body"] for c in result.chunks] + [c.page_content for c in result.chunks]
            out["unverified_numbers"] = find_unverified_numbers(text, sources)

    # Deduplicated citations in rank order
    seen = set()
    for c in result.chunks:
        label = citation(c.metadata)
        if label not in seen:
            seen.add(label)
            out["citations"].append({"label": label, "title": c.metadata["title"], "doc_id": c.metadata["doc_id"]})

    out["latency_ms"] = int((time.time() - started) * 1000)
    return out
