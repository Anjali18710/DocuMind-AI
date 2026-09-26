"""
knowledge_base.py
-----------------
Glue between storage and search: loads the active documents from the
store, builds (or loads the cached) FAISS index, and returns a ready
HybridRetriever.
"""

from typing import List

from langchain_core.documents import Document

from rag.ingestion import build_chunks
from rag.retriever import HybridRetriever
from rag.storage import ACTIVE, fingerprint, get_store, seed_if_empty
from rag.vectorstore import all_chunks, build_vectorstore, load_cached, save_cache


def open_store():
    """Connect to the configured store and load the starter SOPs on first run."""
    store = get_store()
    seeded = seed_if_empty(store)
    if seeded:
        print(f"✓ Seeded knowledge base with {seeded} bundled SOP(s)")
    return store


def chunks_for_active_documents(store) -> List[Document]:
    chunks = []
    for doc in store.list_documents(ACTIVE, include_text=True):
        chunks.extend(build_chunks(doc["page_texts"], doc))
    return chunks


def build_retriever(store, use_cache: bool = True) -> HybridRetriever:
    fp = fingerprint(store)
    vectorstore = load_cached(fp) if use_cache else None
    if vectorstore is None:
        chunks = chunks_for_active_documents(store)
        if not chunks:
            return HybridRetriever(None, [])
        vectorstore = build_vectorstore(chunks)
        if use_cache:
            try:
                save_cache(vectorstore, fp)
            except OSError as exc:  # read-only disk: still works, just slower restarts
                print(f"Could not cache index: {exc}")
    return HybridRetriever(vectorstore, all_chunks(vectorstore))
