import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

st.set_page_config(page_title="DocuMind AI", page_icon="🏭", layout="wide")

from chat import admin_enabled, get_retriever, get_store, is_admin, logout, try_login
from page_admin import render_admin
from page_ask import render_ask
from page_checklist import render_checklist
from rag.metadata import format_revision
from rag.pipeline import LANGUAGES
from rag.storage import ACTIVE

# ── Load CSS ──────────────────────────────────────────────
with open(os.path.join(os.path.dirname(__file__), "styles.css"), encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Pages ─────────────────────────────────────────────────
pages = [
    st.Page(render_ask, title="Ask the SOPs", icon="💬", url_path="ask", default=True),
    st.Page(render_checklist, title="Pre-job checklist", icon="✅", url_path="checklist"),
]
if is_admin():
    pages.append(st.Page(render_admin, title="Admin", icon="🛠", url_path="admin"))
page = st.navigation(pages)

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    try:
        retriever = get_retriever()
        departments = retriever.departments
    except Exception as exc:
        st.error(f"Knowledge base could not be loaded: {exc}")
        departments = []

    st.markdown("## 🔎 Search options")
    dept = st.selectbox("Department", ["All departments"] + departments, key="dept_filter")
    st.session_state.department = None if dept == "All departments" else dept
    st.radio("Answer language", list(LANGUAGES), key="language_choice",
             help="Auto answers in Hindi when the question is typed in Hindi.")

    st.divider()
    active_docs = sorted(get_store().list_documents(ACTIVE), key=lambda d: d.get("sop_no") or d["filename"])
    with st.expander(f"📚 Knowledge base ({len(active_docs)} SOPs)"):
        for d in active_docs:
            st.markdown(
                f"📄 **{d.get('sop_no') or d['filename']}** · {format_revision(d['revision'])}  \n"
                f"<span class='muted'>{d['title']} — {d['department']}</span>",
                unsafe_allow_html=True,
            )

    st.divider()
    if is_admin():
        st.success("Signed in as admin")
        if st.button("Sign out", use_container_width=True):
            logout()
            st.rerun()
    elif admin_enabled():
        with st.expander("🔐 Admin sign-in"):
            with st.form("admin_login", border=False):
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Sign in", use_container_width=True):
                    if try_login(pw):
                        st.rerun()
                    else:
                        st.error("Incorrect password")
    else:
        st.caption("🔐 Admin tools are off. Set ADMIN_PASSWORD to enable document upload and the dashboard.")

page.run()
