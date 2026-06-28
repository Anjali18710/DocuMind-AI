"""
embeddings.py
-------------
Sets up the embedding model (local, no API key required).
Uses HuggingFace sentence-transformers via LangChain.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Returns a HuggingFace embedding model.
    Model is downloaded once and cached locally.
    """
    print(f"✓ Loading embedding model: {EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return embeddings