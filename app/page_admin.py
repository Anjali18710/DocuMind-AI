"""Admin page — document control and usage insights. Only shown after admin sign-in."""

import pandas as pd
import streamlit as st

from chat import get_store, is_admin
from rag.ingestion import ocr_available
from rag.metadata import format_revision
from rag.storage import ACTIVE, SUPERSEDED, add_pdf, delete_document


def _documents_tab(store):
    if store.kind == "Local folder":
        st.info(
            "Documents are stored in a local folder. On Streamlit Community Cloud this folder is wiped "
            "on every restart — set MONGODB_URI to keep uploads permanently.",
            icon="💾",
        )
    if not ocr_available():
        st.caption("OCR is not available on this machine, so scanned PDFs cannot be read.")

    st.subheader("Upload SOPs")
    st.caption(
        "The SOP No and revision are read from the document header. Uploading a higher revision of an "
        "existing SOP replaces it automatically; the older revision is kept in the history below."
    )
    files = st.file_uploader("PDF files", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    if files and st.button("➕ Add to knowledge base", type="primary"):
        for f in files:
            with st.spinner(f"Processing {f.name}..."):
                result = add_pdf(store, f.getvalue(), f.name, uploaded_by="admin")
            (st.success if result["ok"] else st.error)(result["message"])

    docs = store.list_documents()
    active = [d for d in docs if d["status"] == ACTIVE]
    superseded = [d for d in docs if d["status"] == SUPERSEDED]

    st.subheader(f"Active documents ({len(active)})")
    if active:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "SOP No": d.get("sop_no") or "—",
                        "Title": d["title"],
                        "Department": d["department"],
                        "Revision": format_revision(d["revision"]),
                        "Date": d.get("date") or "—",
                        "Pages": d.get("pages"),
                        "OCR pages": d.get("ocr_pages", 0),
                        "File": d["filename"],
                    }
                    for d in sorted(active, key=lambda d: d.get("sop_no") or d["filename"])
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )

        labels = {
            f"{d.get('sop_no') or d['filename']} · {format_revision(d['revision'])} · {d['title']}": d
            for d in active
        }
        choice = st.selectbox("Select a document", list(labels))
        doc = labels[choice]
        c1, c2 = st.columns(2)
        c1.download_button(
            "⬇ Download original PDF", store.get_pdf(doc["doc_id"]), file_name=doc["filename"],
            mime="application/pdf", use_container_width=True,
        )
        with c2.popover("🗑 Delete document", use_container_width=True):
            st.write(f"Delete **{choice}**?")
            if doc.get("supersedes"):
                st.caption("The previous revision will become active again.")
            if st.button("Yes, delete it", type="primary"):
                st.success(delete_document(store, doc["doc_id"]))
                st.rerun()

    if superseded:
        st.subheader(f"Revision history ({len(superseded)} superseded)")
        by_id = {d["doc_id"]: d for d in docs}
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "SOP No": d.get("sop_no"),
                        "Revision": format_revision(d["revision"]),
                        "Dated": d.get("date"),
                        "Replaced by": format_revision(by_id[d["superseded_by"]]["revision"])
                        if d.get("superseded_by") in by_id else "—",
                        "Superseded on": (d.get("superseded_at") or "")[:10],
                        "File": d["filename"],
                    }
                    for d in superseded
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )


def _insights_tab(store):
    queries = store.list_queries()
    if not queries:
        st.info("No questions have been asked yet.")
        return
    df = pd.DataFrame(queries)
    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    total = len(df)
    refused = df["refused"].fillna(False).astype(bool)
    rated = df["feedback"].dropna() if "feedback" in df else pd.Series(dtype=float)
    flagged = df["unverified_numbers"].apply(lambda x: bool(x) if isinstance(x, list) else False)

    c = st.columns(4)
    c[0].metric("Questions asked", total)
    c[1].metric("Answered from SOPs", f"{(~refused).mean():.0%}")
    c[2].metric("👍 rate", f"{rated.mean():.0%}" if len(rated) else "—", help=f"{len(rated)} rated answers")
    c[3].metric("Number warnings", int(flagged.sum()), help="Answers where a number was not found in the SOP text")

    left, right = st.columns(2)
    with left:
        st.markdown("**Questions per day**")
        per_day = df.set_index("ts").resample("D").size().rename("questions")
        per_day.index = per_day.index.strftime("%d %b")
        st.bar_chart(per_day)
    with right:
        st.markdown("**Most-asked-about departments**")
        dept = df.loc[~refused, "top_department"].dropna().value_counts().rename("questions")
        st.bar_chart(dept, horizontal=True)

    st.subheader("📭 Questions the SOPs could not answer")
    st.caption("These show where documentation is missing or unclear — useful input for the next SOP revision.")
    gaps = df[refused]
    if gaps.empty:
        st.write("None so far.")
    else:
        grouped = (
            gaps.assign(q=gaps["question"].str.strip().str.lower())
            .groupby("q")
            .agg(times_asked=("question", "size"), last_asked=("ts", "max"), example=("question", "first"))
            .sort_values(["times_asked", "last_asked"], ascending=False)
            .reset_index(drop=True)[["example", "times_asked", "last_asked"]]
            .rename(columns={"example": "Question", "times_asked": "Times asked", "last_asked": "Last asked"})
        )
        st.dataframe(grouped, hide_index=True, use_container_width=True)

    st.subheader("👎 Answers marked unhelpful")
    if "feedback" in df and (df["feedback"] == 0).any():
        bad = df[df["feedback"] == 0][["ts", "question", "top_sop", "model"]]
        st.dataframe(bad.rename(columns={"ts": "When", "question": "Question", "top_sop": "Top SOP", "model": "Model"}),
                     hide_index=True, use_container_width=True)
    else:
        st.write("None so far.")

    st.download_button(
        "⬇ Download full query log (CSV)",
        df.drop(columns=["citations"], errors="ignore").to_csv(index=False).encode("utf-8"),
        file_name="documind_query_log.csv",
        mime="text/csv",
    )


def render_admin():
    if not is_admin():
        st.error("Admin sign-in required.")
        return
    store = get_store()
    st.title("🛠 Admin")
    st.caption(f"Storage: {store.kind}")
    docs_tab, insights_tab = st.tabs(["📂 Documents", "📊 Usage insights"])
    with docs_tab:
        _documents_tab(store)
    with insights_tab:
        _insights_tab(store)
