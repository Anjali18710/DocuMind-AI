"""
embeddings.py
-------------
Sets up the embedding model (runs locally on CPU, no API key required).
The default model is multilingual, so a question in Hindi lands close to
the English SOP text that answers it.
"""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """Load the embedding model once per process (downloaded and cached on first use)."""
    print(f"✓ Loading embedding model: {EMBEDDING_MODEL}")
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        # Normalised vectors → inner product == cosine similarity (0..1),
        # which the confidence gate in retriever.py relies on.
        encode_kwargs={"normalize_embeddings": True},
    )
