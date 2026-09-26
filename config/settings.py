"""
settings.py
-----------
Central configuration. Every value can be overridden with an environment
variable, a local `.env` file, or Streamlit secrets (`.streamlit/secrets.toml`
locally, or the Secrets box on Streamlit Community Cloud).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Project root = parent of this config/ folder. Used to anchor all
# relative paths so the app works regardless of the cwd it's launched from.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _get(name: str, default=None):
    """Read a setting from env vars first, then Streamlit secrets."""
    value = os.getenv(name)
    if value not in (None, ""):
        return value
    try:
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        # No secrets file / not running under Streamlit — that's fine.
        pass
    return default


def _get_bool(name: str, default: bool) -> bool:
    return str(_get(name, str(default))).strip().lower() in ("1", "true", "yes", "on")


def _get_float(name: str, default: float) -> float:
    try:
        return float(_get(name, default))
    except (TypeError, ValueError):
        return default


# ── API Keys ──────────────────────────────────────────────
GROQ_API_KEY = _get("GROQ_API_KEY")
GEMINI_API_KEY = _get("GEMINI_API_KEY")

# ── LLM Config ────────────────────────────────────────────
# "groq"   → Groq first, Gemini automatically used if Groq fails
# "ollama" → fully local model through Ollama (no document text leaves the machine)
LLM_PROVIDER = _get("LLM_PROVIDER", "groq").lower()
GROQ_MODEL = _get("GROQ_MODEL", "openai/gpt-oss-120b")
# "-latest" alias always points at Google's current Flash model, so the
# fallback does not break again when an older version is retired.
GEMINI_MODEL = _get("GEMINI_MODEL", "gemini-flash-latest")
OLLAMA_MODEL = _get("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = _get("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 2048
LLM_TIMEOUT_SECONDS = 45

# ── Speech-to-text (voice questions) ──────────────────────
WHISPER_MODEL = _get("WHISPER_MODEL", "whisper-large-v3-turbo")

# ── Embedding Model ───────────────────────────────────────
# Multilingual so that a Hindi question can find an English SOP.
EMBEDDING_MODEL = _get(
    "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# ── Optional reranker (off by default to save memory on the free tier) ──
USE_RERANKER = _get_bool("USE_RERANKER", False)
RERANKER_MODEL = _get("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# ── Storage ───────────────────────────────────────────────
# If MONGODB_URI is set, documents + logs live in MongoDB Atlas and survive
# restarts. Otherwise a local folder is used (fine for development).
MONGODB_URI = _get("MONGODB_URI")
MONGODB_DB = _get("MONGODB_DB", "documind")
SEED_DIR = os.path.join(PROJECT_ROOT, "data", "raw")          # bundled starter SOPs
LOCAL_STORE_DIR = os.path.join(PROJECT_ROOT, "data", "store")  # local fallback store
INDEX_CACHE_DIR = os.path.join(PROJECT_ROOT, ".cache", "faiss_index")

# ── Admin ─────────────────────────────────────────────────
# Upload / delete / dashboard are only shown after logging in with this.
# If it is not set, admin features are disabled entirely.
ADMIN_PASSWORD = _get("ADMIN_PASSWORD")

# ── Ingestion ─────────────────────────────────────────────
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
OCR_ENABLED = _get_bool("OCR_ENABLED", True)
OCR_MIN_CHARS = 40  # pages with less extractable text than this are OCR'd

# ── Retrieval ─────────────────────────────────────────────
TOP_K_RESULTS = 5
CANDIDATES_PER_RETRIEVER = 20   # each retriever returns this many before fusion
RRF_K = 60                      # standard constant for Reciprocal Rank Fusion
# Confidence gate: if neither search finds a strong match, answer
# "not covered" without calling the LLM.
MIN_VECTOR_SIMILARITY = _get_float("MIN_VECTOR_SIMILARITY", 0.35)
MIN_BM25_SCORE = _get_float("MIN_BM25_SCORE", 8.0)

# ── Who to contact when the SOPs don't cover a question ───
REFUSAL_CONTACT = _get(
    "REFUSAL_CONTACT",
    "your Shift In-charge or the Safety & Environment Department (Emergency: Ext. 100)",
)
