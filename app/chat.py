"""
chat.py
-------
Shared, cached resources for the Streamlit pages: the document store,
the search index and the LLM router, plus admin-login helpers.
"""

import hmac
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

from config.settings import ADMIN_PASSWORD
from rag.chain import LLMRouter
from rag.knowledge_base import build_retriever, open_store
from rag.pipeline import answer_question
from rag.storage import fingerprint


@st.cache_resource(show_spinner="Connecting to the document store...")
def get_store():
    return open_store()


@st.cache_resource(show_spinner="Loading knowledge base...", max_entries=2)
def _retriever_for(fp: str):
    # `fp` changes whenever documents are added/replaced/deleted, which makes
    # Streamlit build a fresh index automatically.
    return build_retriever(get_store())


def get_retriever():
    return _retriever_for(fingerprint(get_store()))


@st.cache_resource
def get_llm() -> LLMRouter:
    return LLMRouter()


def ask(question: str, department=None, language_choice: str = "Auto") -> dict:
    result = answer_question(
        question, get_retriever(), get_llm(), department=department, language_choice=language_choice
    )
    try:
        record = {k: v for k, v in result.items() if k not in ("verbatim",)}
        get_store().log_query(record)
    except Exception as exc:  # logging must never break answering
        print(f"Could not log query: {exc}")
    return result


def record_feedback(query_id: str, widget_key: str):
    value = st.session_state.get(widget_key)  # 1 = 👍, 0 = 👎, None = cleared
    try:
        get_store().update_query(query_id, {"feedback": value})
    except Exception as exc:
        print(f"Could not save feedback: {exc}")


# ── Admin login ───────────────────────────────────────────

def admin_enabled() -> bool:
    return bool(ADMIN_PASSWORD)


def is_admin() -> bool:
    return bool(st.session_state.get("is_admin"))


def try_login(password: str) -> bool:
    ok = admin_enabled() and hmac.compare_digest(password.encode(), ADMIN_PASSWORD.encode())
    st.session_state.is_admin = ok
    return ok


def logout():
    st.session_state.is_admin = False
