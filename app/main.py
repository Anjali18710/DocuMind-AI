import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from chat import get_answer

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

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:

    st.markdown("## 📚 Knowledge Base")

    st.markdown("""
📄 **Blast Furnace Shutdown SOP**

📄 **Gas Leak Emergency Response**

📄 **Coke Oven PPE Requirements**
""")

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