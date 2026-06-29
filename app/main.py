import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from chat import get_answer

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🏭",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .source-tag {
        background-color: #1e3a5f;
        color: #7eb8f7;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-family: monospace;
    }
    .stChatMessage { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🏭 DocuMind AI")
st.markdown('<p class="subtitle">SAIL Bokaro Steel Plant &nbsp;|&nbsp; RAG-Powered Document Intelligence</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    use_fallback = st.toggle("Use Gemini (fallback LLM)", value=False)
    st.markdown("---")
    st.markdown("**📚 Indexed Documents**")
    st.markdown("- Blast Furnace Shutdown SOP")
    st.markdown("- Gas Leak Emergency Response")
    st.markdown("- Coke Oven PPE Requirements")
    st.markdown("---")
    st.markdown("**💡 Example Queries**")
    st.markdown("- What is the shutdown protocol for Blast Furnace?")
    st.markdown("- What PPE is required in the coke oven area?")
    st.markdown("- How to handle a gas leak emergency?")
    st.markdown("- What is the CO evacuation threshold?")
    st.markdown("- What are the post-shutdown checks for Blast Furnace?")
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
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
            with st.expander("📄 Sources"):
                for src in msg["sources"]:
                    st.markdown(f'<span class="source-tag">📎 {src}</span>', unsafe_allow_html=True)

# ── Chat Input ────────────────────────────────────────────
if question := st.chat_input("Ask about SOPs, safety guidelines, or procedures..."):

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                result = get_answer(question, use_fallback=use_fallback)
                answer = result["answer"]
                sources = result["sources"]

                st.markdown(answer)

                if sources:
                    with st.expander("📄 Sources"):
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