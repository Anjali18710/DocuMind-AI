"""
main.py
-------
Streamlit UI for DocuMind AI.
Run with: streamlit run app/main.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from chat import get_answer

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🏭",
    layout="centered",
)

# ── Header ────────────────────────────────────────────────
st.title("🏭 DocuMind AI")
st.caption("SAIL Bokaro Steel Plant | Powered by RAG + Groq")
st.markdown("Ask any question about SOPs, safety guidelines, or operational procedures.")
st.divider()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    use_fallback = st.toggle("Use Gemini (fallback LLM)", value=False)
    st.markdown("---")
    st.markdown("**How to use:**")
    st.markdown("1. Type your question below")
    st.markdown("2. Get an instant cited answer")
    st.markdown("3. Check sources at the bottom")
    st.markdown("---")
    st.markdown("**Example queries:**")
    st.markdown("- What is the shutdown protocol for Blast Furnace?")
    st.markdown("- What PPE is required in the coke oven area?")
    st.markdown("- How to handle a gas leak emergency?")

# ── Chat History ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 Sources"):
                for src in msg["sources"]:
                    st.markdown(f"- `{src}`")

# ── Chat Input ────────────────────────────────────────────
if question := st.chat_input("Ask about SOPs or safety guidelines..."):

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
                            st.markdown(f"- `{src}`")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Something went wrong: {e}")