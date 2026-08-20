"""
vectorstore.py
--------------
Handles FAISS: building the vector store from chunks,
persisting it to disk, and loading it back for querying.
"""

import os
import shutil
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from rag.embeddings import get_embedding_model

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FAISS_PATH = os.path.join(_PROJECT_ROOT, "vectorstore", "faiss_index")


def build_vectorstore(chunks: List[Document]) -> FAISS:
    print(f"\n── Building Vector Store ───────────────")
    embeddings = get_embedding_model()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    os.makedirs(os.path.dirname(FAISS_PATH), exist_ok=True)
    vectorstore.save_local(FAISS_PATH)
    print(f"✓ Vector store saved ({len(chunks)} chunks indexed)")
    return vectorstore


def load_vectorstore() -> FAISS:
    embeddings = get_embedding_model()
    vectorstore = FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print(f"✓ Vector store loaded from '{FAISS_PATH}'")
    return vectorstore


def vectorstore_exists() -> bool:
    return os.path.exists(FAISS_PATH)


def add_documents_to_store(chunks: List[Document]) -> FAISS:
    if vectorstore_exists():
        vectorstore = load_vectorstore()
        vectorstore.add_documents(chunks)
        vectorstore.save_local(FAISS_PATH)
        print(f"✓ Added {len(chunks)} chunks to existing vector store")
    else:
        vectorstore = build_vectorstore(chunks)
    return vectorstore


def rebuild_vectorstore_from_data_dir():
    from rag.ingestion import ingest_documents
    from config.settings import DATA_DIR

    if os.path.exists(FAISS_PATH):
        shutil.rmtree(FAISS_PATH)

    try:
        chunks = ingest_documents(DATA_DIR)
    except FileNotFoundError:
        print("No PDFs remain in data directory; vector store cleared.")
        return None

    return build_vectorstore(chunks)