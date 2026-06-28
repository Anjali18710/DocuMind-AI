"""
vectorstore.py
--------------
Handles FAISS: building the vector store from chunks,
persisting it to disk, and loading it back for querying.
"""

import os
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from rag.embeddings import get_embedding_model

FAISS_PATH = "vectorstore/faiss_index"


def build_vectorstore(chunks: List[Document]) -> FAISS:
    print(f"\n── Building Vector Store ───────────────")
    embeddings = get_embedding_model()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    os.makedirs("vectorstore", exist_ok=True)
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