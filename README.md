# DocuMind AI 🏭

**RAG-Powered Document Intelligence for SAIL Bokaro Steel Plant**

DocuMind AI is an internal SOP assistant built during my internship at SAIL (Steel Authority of India Limited), Bokaro Steel Plant. It allows plant personnel to query Standard Operating Procedures and safety guidelines in natural language, with answers grounded strictly in indexed documents.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — llama-3.3-70b-versatile |
| Fallback LLM | Google Gemini |
| Embeddings | HuggingFace — all-MiniLM-L6-v2 |
| Vector Store | FAISS |
| RAG Framework | LangChain |
| UI | Streamlit |

---

## Indexed Documents (v1.0)

- Blast Furnace Shutdown SOP
- Gas Leak Emergency Response
- Coke Oven PPE Requirements

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
    │   └── main.py          # Streamlit UI
    ├── chat.py              # RAG chain + answer generation
    ├── ingest.py            # Document ingestion and FAISS index builder
    ├── data/                # Source SOP documents
    ├── faiss_index/         # Generated vector store (auto-created)
    ├── requirements.txt
    └── README.md

---

*Built during internship at SAIL Bokaro Steel Plant, June 2025*