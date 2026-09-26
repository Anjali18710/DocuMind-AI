"""Ask page — chat with the SOPs (text or voice)."""

import hashlib
import html

import streamlit as st

from chat import ask, record_feedback
from rag.chain import LLMUnavailableError
from rag.voice import transcribe, voice_available

EXAMPLES = [
    "What should I do immediately if I detect a gas leak?",
    "At what CO level must the area be evacuated?",
    "What PPE is mandatory in the coke oven battery?",
    "What does BSP-BF-001 say about stopping ore charging?",
    "गैस रिसाव होने पर पहले क्या करना चाहिए?",
]


def _render_result(result: dict, index: int):
    if result.get("refused"):
        st.warning(result["answer"], icon="📭")
    else:
        if result.get("verbatim"):
            st.markdown("##### 📋 Exact SOP text")
            for block in result["verbatim"]:
                st.markdown(
                    f"<div class='verbatim'><div class='verbatim-cite'>{html.escape(block['citation'])}</div>"
                    f"{html.escape(block['text'])}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("##### 🤖 AI summary")
        st.markdown(result["answer"])
        if result.get("unverified_numbers"):
            nums = ", ".join(result["unverified_numbers"])
            st.error(
                f"**Check before acting:** {nums} — not found in the cited SOP text. "
                "The AI may have made a mistake; confirm against the SOP.",
                icon="⚠️",
            )

    if result.get("citations"):
        with st.expander("📄 Sources", expanded=False):
            for c in result["citations"]:
                st.markdown(
                    f"<span class='source-tag'>📎 {html.escape(c['label'])}</span> "
                    f"<span class='muted'>{html.escape(c['title'])}</span>",
                    unsafe_allow_html=True,
                )

    meta = []
    if result.get("safety_critical"):
        meta.append("🛡 Safety mode")
    if result.get("model"):
        meta.append(result["model"])
    if result.get("latency_ms") is not None:
        meta.append(f"{result['latency_ms'] / 1000:.1f}s")
    if meta:
        st.caption(" · ".join(meta))

    key = f"fb_{result['query_id']}"
    st.feedback("thumbs", key=key, on_change=record_feedback, args=(result["query_id"], key))


def _answer(question: str):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching the SOPs..."):
            try:
                result = ask(
                    question,
                    department=st.session_state.get("department"),
                    language_choice=st.session_state.get("language_choice", "Auto"),
                )
            except LLMUnavailableError as exc:
                st.error(str(exc))
                return
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
                return
        st.session_state.messages.append({"role": "assistant", "result": result})
        _render_result(result, len(st.session_state.messages) - 1)


def render_ask():
    st.markdown(
        """<div class="hero"><h1>🏭 DocuMind AI</h1>
        <h3>SOP &amp; safety assistant for plant personnel</h3>
        <p>Answers only from current SOPs · cites SOP No, revision &amp; page · English / हिन्दी</p></div>""",
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    top = st.columns([3, 1])
    with top[1]:
        if st.button("🗑 Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pop("last_example", None)
            st.session_state.pop("example_pick", None)
            st.rerun()

    if voice_available():
        with top[0].expander("🎤 Ask by voice (English / Hindi)"):
            audio = st.audio_input("Record your question", label_visibility="collapsed")
            if audio is not None:
                data = audio.getvalue()
                digest = hashlib.md5(data).hexdigest()
                if st.session_state.get("last_audio") != digest:
                    st.session_state.last_audio = digest
                    with st.spinner("Transcribing..."):
                        try:
                            st.session_state.pending_question = transcribe(data)
                        except Exception as exc:
                            st.error(f"Could not transcribe audio: {exc}")

    if not st.session_state.messages:
        st.info("👋 Ask about any SOP, safety rule or procedure — type below, use voice, or try one of these:")
        picked = st.pills("Examples", EXAMPLES, label_visibility="collapsed", key="example_pick")
        if picked and st.session_state.get("last_example") != picked:
            st.session_state.last_example = picked
            st.session_state.pending_question = picked

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                _render_result(msg["result"], i)

    typed = st.chat_input("Ask about an SOP, e.g. 'PPE for entering the tuyere area'")
    question = typed or st.session_state.pop("pending_question", None)
    if question and question.strip():
        _answer(question.strip())
