"""
ingest.py
---------
Run this ONCE to index your documents into ChromaDB.
Place PDF files in data/raw/ before running.

Usage:
    python ingest.py
"""

from rag.ingestion import ingest_documents
from rag.vectorstore import build_vectorstore

if __name__ == "__main__":
    print("DocuMind AI — Document Ingestion")
    print("=" * 40)
    chunks = ingest_documents()
    vectorstore = build_vectorstore(chunks)
    print("\n✅ Ingestion complete.")