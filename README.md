# DocuMind AI 🏭
**RAG-Powered Document Intelligence for SAIL Bokaro Steel Plant**

DocuMind AI is an internal SOP assistant built during my internship at SAIL (Steel Authority of India Limited), Bokaro Steel Plant. It allows plant personnel to query Standard Operating Procedures and safety guidelines in natural language, with answers grounded strictly in indexed documents.

**🔗 Live Demo:** [documind-ai-sail.streamlit.app](https://documind-ai-sail.streamlit.app/)

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — openai/gpt-oss-120b |
| Fallback LLM | Google Gemini |
| Embeddings | HuggingFace — all-MiniLM-L6-v2 |
| Vector Store | FAISS |
| RAG Framework | LangChain |
| UI | Streamlit |

---

## Features

- 💬 Natural language Q&A over indexed SOPs and safety documents
- 📤 **Upload your own PDF** — add new documents to the knowledge base at runtime
- 🗑 **Remove documents** — delete a PDF from the knowledge base, with the index automatically rebuilt
- 📄 Source citations — every answer shows which document it came from
- 🔁 Gemini fallback if the primary Groq model is unavailable

---

## Indexed Documents (v1.0)

- Blast Furnace Shutdown SOP
- Gas Leak Emergency Response
- Coke Oven PPE Requirements

*(Additional documents can be added or removed directly from the app's sidebar.)*

---

## How to Run

**1. Clone the repo**

    git clone https://github.com/Anjali18710/DocuMind-AI.git
    cd DocuMind-AI

**2. Create a virtual environment and install dependencies**

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

> On Windows, replace `source venv/bin/activate` with `venv\Scripts\activate`

**3. Set up environment variables**

Create a file named `.env` in the root folder and add your API keys like this:

    GROQ_API_KEY=paste_your_groq_key_here
    GEMINI_API_KEY=paste_your_gemini_key_here

Do not share this file. It is already listed in `.gitignore`.

**4. Run the app**

    streamlit run app/main.py

---

## Project Structure

    DocuMind-AI/
    ├── app/
    │   ├── main.py          # Streamlit UI
    │   └── chat.py          # RAG chain + answer generation
    ├── rag/
    │   ├── ingestion.py      # Document loading and chunking
    │   ├── embeddings.py     # Embedding model setup
    │   ├── vectorstore.py    # FAISS index build/load/update
    │   ├── retriever.py      # Similarity-based retriever
    │   └── chain.py          # LLM + prompt + RAG chain
    ├── config/
    │   └── settings.py       # Central config (paths, models, API keys)
    ├── data/raw/             # Source PDF documents
    ├── vectorstore/faiss_index/  # Generated vector store (auto-created)
    ├── ingest.py              # One-time bulk ingestion script
    ├── requirements.txt
    └── README.md

---

*Built during internship at SAIL Bokaro Steel Plant, June 2025*