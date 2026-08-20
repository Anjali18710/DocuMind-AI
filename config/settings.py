import os
from dotenv import load_dotenv

load_dotenv()

# Project root = parent of this config/ folder. Used to anchor all
# relative paths so the app works regardless of the cwd it's launched from.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ── API Keys ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ── LLM Config ────────────────────────────────────────────
PRIMARY_LLM = "groq"
GROQ_MODEL = "openai/gpt-oss-120b"
GEMINI_MODEL = "gemini-1.5-flash"

# ── Embedding Model ───────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ── ChromaDB ──────────────────────────────────────────────
CHROMA_PERSIST_DIR = "vectorstore"
CHROMA_COLLECTION_NAME = "documind_docs"

# ── Ingestion ─────────────────────────────────────────────
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# ── Retrieval ─────────────────────────────────────────────
TOP_K_RESULTS = 5