"""
vectorstore.py
--------------
Handles ChromaDB: building the vector store from chunks,
persisting it to disk, and loading it back for querying.
"""

import os
from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from config.settings import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from rag.embeddings import get_embedding_model


def build_vectorstore(chunks: List[Document]) -> Chroma:
    """
    Embeds document chunks and stores them in ChromaDB.
    Persists to disk at CHROMA_PERSIST_DIR.
    """
    print(f"\n── Building Vector Store ───────────────")
    embeddings = get_embedding_model()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print(f"✓ Vector store saved to '{CHROMA_PERSIST_DIR}' ({len(chunks)} chunks indexed)")
    return vectorstore


def load_vectorstore() -> Chroma:
    """
    Loads an existing ChromaDB vector store from disk.
    """
    embeddings = get_embedding_model()
    vectorstore = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    print(f"✓ Vector store loaded from '{CHROMA_PERSIST_DIR}'")
    return vectorstore


def vectorstore_exists() -> bool:
    """Check if a persisted vector store already exists."""
    return os.path.exists(CHROMA_PERSIST_DIR) and len(os.listdir(CHROMA_PERSIST_DIR)) > 0