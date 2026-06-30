"""
retriever.py
------------
Wraps the FAISS vector store with a similarity-based retriever.
Returns top-K relevant chunks for a given query.
"""

from langchain_community.vectorstores import FAISS
from langchain_core.retrievers import BaseRetriever
from config.settings import TOP_K_RESULTS


def get_retriever(vectorstore: FAISS) -> BaseRetriever:
    """
    Returns a retriever that fetches top-K similar chunks.
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K_RESULTS},
    )
    print(f"✓ Retriever ready (top_k={TOP_K_RESULTS})")
    return retriever