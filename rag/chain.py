"""
chain.py
--------
The language-model side of the RAG pipeline.

* LLMRouter tries the providers in order and falls back automatically:
  Groq (primary) → Gemini (fallback). If LLM_PROVIDER=ollama, a local
  model is used instead and no document text leaves the machine.
* Prompt builders for Q&A and for the pre-job checklist.
"""

from typing import List, Tuple

from langchain_core.documents import Document

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_MAX_TOKENS,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)
from rag.metadata import format_revision

NOT_FOUND_TOKEN = "NOT_FOUND"


class LLMUnavailableError(RuntimeError):
    pass


def _make_groq(json_mode: bool = False):
    from langchain_groq import ChatGroq

    extra = {}
    if "gpt-oss" in GROQ_MODEL:
        # gpt-oss "thinks" before answering and that thinking uses up the
        # token budget; low effort keeps room for the actual answer.
        extra["reasoning_effort"] = "low"
    if json_mode:
        # Groq's JSON mode guarantees syntactically valid JSON.
        extra["model_kwargs"] = {"response_format": {"type": "json_object"}}
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        timeout=LLM_TIMEOUT_SECONDS,
        max_retries=1,
        **extra,
    )


def _make_gemini(json_mode: bool = False):
    from langchain_google_genai import ChatGoogleGenerativeAI

    extra = {"response_mime_type": "application/json"} if json_mode else {}
    return ChatGoogleGenerativeAI(
        google_api_key=GEMINI_API_KEY,
        model=GEMINI_MODEL,
        temperature=LLM_TEMPERATURE,
        max_output_tokens=LLM_MAX_TOKENS,
        timeout=LLM_TIMEOUT_SECONDS,
        max_retries=1,
        **extra,
    )


def _make_ollama(json_mode: bool = False):
    from langchain_ollama import ChatOllama

    extra = {"format": "json"} if json_mode else {}
    return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=LLM_TEMPERATURE, **extra)


def configured_providers() -> List[Tuple[str, str, callable]]:
    """(label, model name, factory) for every provider that has credentials, in priority order."""
    if LLM_PROVIDER == "ollama":
        return [("Ollama (local)", OLLAMA_MODEL, _make_ollama)]
    providers = []
    if GROQ_API_KEY:
        providers.append(("Groq", GROQ_MODEL, _make_groq))
    if GEMINI_API_KEY:
        providers.append(("Gemini", GEMINI_MODEL, _make_gemini))
    return providers


class LLMRouter:
    """Calls the first provider that works; later ones are automatic fallbacks."""

    def __init__(self, providers=None):
        self.providers = providers if providers is not None else configured_providers()
        self._clients = {}

    def _client(self, label, factory, json_mode=False):
        key = (label, json_mode)
        if key not in self._clients:
            self._clients[key] = factory(json_mode=True) if json_mode else factory()
        return self._clients[key]

    def generate(self, prompt: str, json_mode: bool = False) -> Tuple[str, str]:
        """
        Return (answer text, "Provider · model" that produced it).
        json_mode=True asks the provider to return strictly valid JSON.
        """
        if not self.providers:
            raise LLMUnavailableError(
                "No language model is configured. Add GROQ_API_KEY and/or GEMINI_API_KEY "
                "to your .env file or Streamlit secrets."
            )
        errors = []
        for position, (label, model, factory) in enumerate(self.providers):
            try:
                response = self._client(label, factory, json_mode).invoke(prompt)
                text = _text_of(response)
                if not text.strip():
                    raise RuntimeError("empty response")
                used = f"{label} · {model}"
                if position > 0:
                    used += " (automatic fallback)"
                return text.strip(), used
            except Exception as exc:  # network error, rate limit, bad key, retired model...
                print(f"✗ {label} failed: {exc}")
                errors.append(f"{label}: {exc}")
        raise LLMUnavailableError("All language models failed. " + " | ".join(errors))


def _text_of(response) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, list):  # some providers return content blocks
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in content
        )
    return str(content)


# ── Citations & context ───────────────────────────────────

def citation(meta: dict, with_section: bool = True) -> str:
    parts = [meta.get("sop_no") or meta.get("source"), format_revision(meta.get("revision", 0)), f"p.{meta.get('page')}"]
    if with_section and meta.get("section") and meta["section"] != "Header":
        parts.append(meta["section"])
    return " · ".join(str(p) for p in parts if p)


def format_context(chunks: List[Document]) -> str:
    blocks = []
    for doc in chunks:
        m = doc.metadata
        blocks.append(
            f"[{citation(m, with_section=False)}] {m['title']} — {m.get('section', '')}\n{m['body']}"
        )
    return "\n\n---\n\n".join(blocks)


# ── Prompts ───────────────────────────────────────────────

QA_PROMPT = """You are DocuMind, the SOP assistant for plant personnel at Bokaro Steel Plant.
Answer the question using ONLY the SOP excerpts below.

Rules:
- If the excerpts do not contain the answer, reply with exactly: {not_found}
- Copy every number, limit, distance, extension number and unit EXACTLY as written in the excerpts. Never estimate or convert.
- After each fact, cite its source in square brackets exactly as shown in the excerpt header, e.g. [BSP-GS-004 · Rev 03 · p.1].
- {style}
- Write the answer in {language}. Keep SOP numbers, gas names, units and extension numbers unchanged.

SOP excerpts:
{context}

Question: {question}

Answer:"""

SAFETY_STYLE = (
    "This is a safety-critical question: give the steps in the same order as the SOP, "
    "as a numbered list, and do not leave out any warning or 'Do NOT' instruction."
)
NORMAL_STYLE = "Be concise and precise."


def build_qa_prompt(question: str, chunks: List[Document], language: str, safety: bool) -> str:
    return QA_PROMPT.format(
        not_found=NOT_FOUND_TOKEN,
        style=SAFETY_STYLE if safety else NORMAL_STYLE,
        language=language,
        context=format_context(chunks),
        question=question,
    )


CHECKLIST_PROMPT = """You are preparing a pre-job safety checklist for plant personnel.
Task: {task}
Area / equipment: {area}

Using ONLY the numbered SOP excerpts below, list what the worker must check or do BEFORE and DURING this job.
Return ONLY valid JSON, no other text, in this format:
{{"title": "...", "sections": [{{"heading": "PPE required", "items": [{{"text": "...", "source": 3}}]}}]}}

Rules:
- Use these section headings where relevant: "Permits & authorisation", "PPE required", "Hazards to watch for", "Before starting", "During the job", "Emergency contacts".
- Every item must be supported by the excerpt whose number you give in "source". Do not add anything that is not in the excerpts.
- Copy numbers and units exactly. Keep each item short (one line).
- If the excerpts do not cover this task at all, return {{"title": "{not_found}", "sections": []}}

Excerpts:
{context}
"""


def build_checklist_prompt(task: str, area: str, chunks: List[Document]) -> str:
    numbered = []
    for i, doc in enumerate(chunks, start=1):
        m = doc.metadata
        numbered.append(f"({i}) [{citation(m, with_section=False)}] {m['title']} — {m.get('section', '')}\n{m['body']}")
    return CHECKLIST_PROMPT.format(
        task=task, area=area or "not specified", context="\n\n".join(numbered), not_found=NOT_FOUND_TOKEN
    )
