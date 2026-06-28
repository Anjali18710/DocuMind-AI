"""
ingestion.py
------------
Loads PDF documents from data/raw/, splits them into chunks,
and returns LangChain Document objects ready for embedding.
"""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from config.settings import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def load_pdfs(data_dir: str = DATA_DIR) -> List[Document]:
    """Load all PDFs from the data directory."""
    docs = []
    pdf_files = list(Path(data_dir).glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in '{data_dir}'.")

    for pdf_path in pdf_files:
        print(f"  Loading: {pdf_path.name}")
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()

        for page in pages:
            page.metadata["source"] = pdf_path.name

        docs.extend(pages)

    print(f"\n✓ Loaded {len(docs)} pages from {len(pdf_files)} PDF(s)")
    return docs


def split_documents(docs: List[Document]) -> List[Document]:
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"✓ Split into {len(chunks)} chunks")
    return chunks


def ingest_documents(data_dir: str = DATA_DIR) -> List[Document]:
    """Full ingestion pipeline: load → split → return chunks."""
    print(f"\n── Ingestion Pipeline ──────────────────")
    docs = load_pdfs(data_dir)
    chunks = split_documents(docs)
    return chunks