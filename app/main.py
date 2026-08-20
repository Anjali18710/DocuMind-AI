import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from chat import get_answer
from config.settings import DATA_DIR
from rag.ingestion import ingest_uploaded_file
from rag.vectorstore import add_documents_to_store, rebuild_vectorstore_from_data_dir

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🏭",
    layout="wide",
)

# ── Load CSS ──────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "styles.css")

with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Hero Section ──────────────────────────────────────────

st.markdown("""
<div class="hero">

<h1>🏭 DocuMind AI</h1>

<h3>RAG-Powered Document Intelligence</h3>

<p>
Search • Safety Manuals • SOPs • Operational Procedures
</p>

</div>
""", unsafe_allow_html=True)

st.divider()


def get_indexed_pdf_names():
    """List PDFs currently in data/raw/, so the sidebar reflects reality
    instead of a hardcoded list."""
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted(f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf"))


# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:

    st.markdown("## 📚 Knowledge Base")

    indexed_pdfs = get_indexed_pdf_names()
    if indexed_pdfs:
        for name in indexed_pdfs:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"📄 **{name}**")
            with col2:
                delete_clicked = st.button("🗑", key=f"del_{name}", help=f"Remove {name}")

            if delete_clicked:
                with st.spinner(f"Removing {name}..."):
                    file_path = os.path.join(DATA_DIR, name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    rebuild_vectorstore_from_data_dir()
                    st.cache_resource.clear()
                st.success(f"Removed {name}")
                st.rerun()
    else:
        st.caption("No documents indexed yet.")

    st.divider()

    st.markdown("## 📤 Upload a PDF")
    uploaded_file = st.file_uploader(
        "Add a new document to the knowledge base",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        if st.button("➕ Add to Knowledge Base", use_container_width=True):
            with st.spinner(f"Processing {uploaded_file.name}..."):
                os.makedirs(DATA_DIR, exist_ok=True)
                save_path = os.path.join(DATA_DIR, uploaded_file.name)

                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                try:
                    chunks = ingest_uploaded_file(save_path, uploaded_file.name)
                    add_documents_to_store(chunks)
                    st.cache_resource.clear()
                    st.success(f"✓ {uploaded_file.name} added to the knowledge base!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not process this PDF: {e}")

    st.divider()

    st.markdown("## ⚙ AI Settings")

    use_fallback = st.toggle(
        "Use Gemini as fallback",
        value=False,
        help="Automatically switches to Gemini if the primary model is unavailable."
    )

    st.divider()

    st.markdown("## 💡 Try Asking")

    st.markdown("""
- Shutdown procedure for Blast Furnace

- PPE requirements in Coke Oven

- Gas leak emergency protocol

- CO evacuation threshold
""")

    st.divider()

    if st.button("🗑 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Chat History ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.info("👋 Ask me anything about SAIL SOPs, safety guidelines, or operational procedures.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 Source Documents ",expanded=False):
                for src in msg["sources"]:
                    st.markdown(f'<span class="source-tag">📎 {src}</span>', unsafe_allow_html=True)

# ── Chat Input ────────────────────────────────────────────
if question := st.chat_input("How can I help you today ?"):

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching knowledge base...."):
            try:
                result = get_answer(question, use_fallback=use_fallback)
                answer = result["answer"]
                sources = result["sources"]

                st.markdown(answer)

                if sources:
                    with st.expander("📄 Source Documents",expanded=False):
                        for src in sources:
                            st.markdown(f'<span class="source-tag">📎 {src}</span>', unsafe_allow_html=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Something went wrong: {e}")