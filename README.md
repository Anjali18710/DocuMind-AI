# DocuMind AI 🏭
**SOP & safety assistant for plant personnel — built during my internship at SAIL Bokaro Steel Plant**

DocuMind lets shop-floor staff ask questions about Standard Operating Procedures in English or Hindi (typed or spoken) and get answers that are **grounded in the current revision of the SOP, cite the exact SOP number, revision and page, and are checked for errors before they are shown**.

**🔗 Live Demo:** [documind-ai-sail.streamlit.app](https://documind-ai-sail.streamlit.app/)

---

## Why it is built this way

In a steel plant a wrong number in an answer ("evacuate at 75 ppm" instead of 50) can hurt someone, and an outdated SOP is as dangerous as a missing one. So DocuMind is designed around four things:

| Need | What DocuMind does |
|---|---|
| **Trustworthy** | Safety questions show the SOP's **exact wording** next to the AI summary. Every number in an AI answer is **checked against the source text** and flagged if it isn't there. If the SOPs don't cover a question, it says so and names who to contact instead of guessing. |
| **Current** | SOP No, revision and date are read from each document. Uploading a newer revision **automatically supersedes** the old one; answers only come from active revisions, and every answer shows which revision it used. |
| **Usable on the shop floor** | Hindi and English questions and answers, **voice input**, and a **pre-job checklist generator** that turns the relevant SOPs into a printable tick-list. |
| **Useful to management** | Admins see which questions the SOPs **couldn't answer** (documentation gaps), which answers were marked unhelpful, and which departments' SOPs are used most. |

---

## Features

**For plant personnel**
- 💬 Natural-language Q&A over SOPs, with citations like `BSP-GS-004 · Rev 03 · p.1 · 4. DETECTION THRESHOLDS`
- 🛡 **Safety mode** — emergency / PPE / hazard questions show the verbatim SOP steps, then an ordered AI summary
- ⚠️ **Number check** — flags any number in the answer that does not appear in the cited SOP text
- 📭 **Honest "not covered"** — weak matches are refused *before* calling the LLM; the LLM can also refuse
- 🇮🇳 **Hindi / English** — multilingual embeddings, so a Hindi question finds an English SOP; answer language selectable
- 🎤 **Voice questions** — Whisper speech-to-text via Groq (English, Hindi, Hinglish)
- ✅ **Pre-job checklist** — describe the job, get a checklist of permits, PPE, hazards and precautions, each line cited; download as PDF
- 🏷 Department filter

**For admins** (password-protected)
- 📤 Upload SOPs (bulk); duplicates and older revisions are rejected with a clear message
- 🔁 Revision history; deleting a revision restores the previous one
- 🖨 Scanned PDFs are read with OCR (Tesseract)
- 📊 Usage insights: questions asked, % answered, 👍 rate, number warnings, unanswered questions, unhelpful answers, CSV export

**Under the hood**
- 🔎 **Hybrid retrieval** — FAISS (meaning) + BM25 (exact keywords such as `BSP-GS-004`, `LDG`, `IS 2925`) merged with Reciprocal Rank Fusion; optional cross-encoder reranker
- 🔁 **Automatic LLM fallback** — Groq → Gemini if Groq fails; or **fully local** with Ollama
- 💾 **Persistent storage** — MongoDB Atlas (documents in GridFS, metadata, logs); local-folder fallback for development
- 🧪 **Evaluation harness** and **30 automated tests**

---

## How a question is answered

```
question (typed / spoken → Whisper)
   │
   ▼
Hybrid search ── FAISS (multilingual embeddings) ──┐
   │          └─ BM25 (keywords, SOP codes) ────────┴─► Reciprocal Rank Fusion ─► (optional reranker)
   ▼
Confidence gate ── weak match? ──► "Not covered in current SOPs — contact …"  (no LLM call)
   │
   ▼
Safety question? ──► pull exact SOP text for display
   │
   ▼
LLM (Groq → Gemini fallback, or Ollama) with strict prompt: copy numbers exactly, cite every fact
   │
   ▼
Number check against sources ──► warning if any number isn't in the SOP text
   │
   ▼
Answer + citations + feedback buttons  → logged for the admin dashboard
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — `openai/gpt-oss-120b` |
| Fallback LLM | Google Gemini (`gemini-flash-latest`), automatic |
| Local / on-prem LLM (optional) | Ollama |
| Speech-to-text | Groq Whisper (`whisper-large-v3-turbo`) |
| Embeddings | HuggingFace `paraphrase-multilingual-MiniLM-L12-v2` (runs locally) |
| Retrieval | FAISS + BM25 (`rank-bm25`), Reciprocal Rank Fusion, optional cross-encoder reranker |
| RAG framework | LangChain |
| PDF / OCR | pypdf, pypdfium2, Tesseract (`pytesseract`) |
| Storage | MongoDB Atlas (GridFS) · local folder fallback |
| UI | Streamlit (multi-page) |
| PDF export | fpdf2 |
| Testing | pytest, mongomock |

---

## Running locally

**1. Clone and install**

    git clone https://github.com/Anjali18710/DocuMind-AI.git
    cd DocuMind-AI
    python -m venv venv
    source venv/bin/activate          # Windows: venv\Scripts\activate
    pip install -r requirements.txt

**2. Add your keys** — create a `.env` file in the project folder (see `.env.example`):

    GROQ_API_KEY=paste_your_groq_key_here
    GEMINI_API_KEY=paste_your_gemini_key_here
    ADMIN_PASSWORD=choose-a-password
    # MONGODB_URI=mongodb+srv://...     (optional locally)

**3. Run**

    streamlit run app/main.py

On first start the 19 bundled SOPs in `data/raw/` are loaded and indexed (the embedding model downloads once, ~470 MB).

**Optional — OCR for scanned PDFs:** install Tesseract ([Windows installer](https://github.com/UB-Mannheim/tesseract/wiki), `brew install tesseract`, or `apt install tesseract-ocr`). Without it, scanned PDFs are rejected with a clear message.

**Optional — fully on-premises:** install [Ollama](https://ollama.com), run `ollama pull llama3.1:8b`, and set `LLM_PROVIDER=ollama`. Embeddings already run locally, so no document text leaves the machine (voice input is disabled in this mode).

### Try the revision workflow
Sign in as admin → **Admin → Documents** → upload `data/samples/GAS_LEAK_EMERGENCY_SOP_Rev04.pdf`. Rev 03 is marked superseded, and asking *"At what CO level must we evacuate?"* now answers **35 ppm (Rev 04)** instead of 50 ppm. Delete Rev 04 to roll back.

---

## Configuration

All settings live in `config/settings.py` and can be overridden in `.env` or Streamlit secrets.

| Setting | Default | Purpose |
|---|---|---|
| `GROQ_API_KEY`, `GEMINI_API_KEY` | — | LLM providers (Gemini is used automatically if Groq fails) |
| `MONGODB_URI` | — | Persistent storage; without it a local folder is used |
| `ADMIN_PASSWORD` | — | Enables the Admin page; admin features are hidden if unset |
| `LLM_PROVIDER` | `groq` | `ollama` for a fully local model |
| `EMBEDDING_MODEL` | multilingual MiniLM | Any sentence-transformers model |
| `USE_RERANKER` | `false` | Cross-encoder reranking (English questions) |
| `MIN_VECTOR_SIMILARITY` / `MIN_BM25_SCORE` | `0.35` / `8.0` | Confidence gate — tune with the evaluation script |

---

## Evaluation

`eval/questions.json` holds **54 test questions** with known answers: 45 English, 3 Hindi, and 6 that no SOP covers (the app should refuse them).

    python -m eval.run_eval          # retrieval only: compares BM25 vs vector vs hybrid (no API key needed)
    python -m eval.run_eval --llm    # also checks full answers through the LLM

It reports Hit@1, Hit@5, MRR, correct refusals, false refusals and answer accuracy, and saves them to `eval/results.md`.

## Tests

    pip install -r requirements-dev.txt
    pytest

30 tests covering header parsing, OCR, revision rules, MongoDB storage (mocked), hybrid search, the confidence gate, safety detection, the number check, LLM fallback, Hindi handling and checklist grounding. They run offline with a fake embedding model and a fake LLM.

---

## Deploying on Streamlit Community Cloud

1. Main file: `app/main.py`, Python 3.11.
2. **App settings → Secrets**: paste the keys from `.streamlit/secrets.toml.example`.
3. Set `MONGODB_URI` (a free MongoDB Atlas cluster is enough). Streamlit Cloud's disk is wiped on every restart, so without it uploads and logs are lost.
4. `packages.txt` installs Tesseract for OCR automatically.

---

## Project Structure

    DocuMind-AI/
    ├── app/
    │   ├── main.py             # Entry point: navigation, sidebar, admin sign-in
    │   ├── page_ask.py         # Q&A page (text + voice, safety mode, feedback)
    │   ├── page_checklist.py   # Pre-job checklist generator
    │   ├── page_admin.py       # Document control + usage insights
    │   ├── chat.py             # Cached resources shared by the pages
    │   └── styles.css
    ├── rag/
    │   ├── pipeline.py         # answer_question(): the full flow, shared by app and eval
    │   ├── retriever.py        # Hybrid FAISS + BM25 search, RRF, reranker, confidence gate
    │   ├── vectorstore.py      # FAISS build + on-disk cache
    │   ├── embeddings.py       # Multilingual embedding model
    │   ├── ingestion.py        # PDF text + OCR, section-aware chunking
    │   ├── metadata.py         # SOP header parsing (SOP No, revision, dept, date)
    │   ├── storage.py          # MongoDB / local storage, revision rules
    │   ├── knowledge_base.py   # Store → index glue
    │   ├── chain.py            # LLM router with fallback, prompts, citations
    │   ├── safety.py           # Safety-question detection, number check
    │   ├── checklist.py        # Checklist generation + PDF export
    │   └── voice.py            # Whisper speech-to-text
    ├── config/settings.py      # All configuration
    ├── data/raw/               # Bundled SOPs (loaded on first run)
    ├── data/samples/           # Rev 04 of the gas-leak SOP, for the revision demo
    ├── eval/                   # Test questions + evaluation script
    ├── tests/                  # pytest suite
    ├── scripts/                # Generator for the illustrative sample SOPs
    ├── ingest.py               # Optional CLI: pre-build index / bulk-add a folder
    ├── requirements.txt
    └── packages.txt            # System packages for Streamlit Cloud (Tesseract)

---

## About the documents

The three original SOPs (blast furnace shutdown, coke oven PPE, gas leak response) were prepared during the internship. The other 16 documents in `data/raw/` and the Rev 04 sample are **illustrative samples** written for this demo, modelled on typical integrated-steel-plant practice, and marked as such on every page. They are not official SAIL documents and must not be used as real operating procedures.
