"""
ingest.py
---------
Optional command-line helper. The app loads documents by itself, so you
only need this to pre-build the index or to bulk-add a folder of PDFs.

Usage:
    python ingest.py                  # load bundled SOPs (first run) and build the index
    python ingest.py path/to/folder   # also add every PDF in that folder
"""

import sys
from pathlib import Path

from rag.knowledge_base import build_retriever, open_store
from rag.storage import ACTIVE, add_pdf

if __name__ == "__main__":
    print("DocuMind AI — Document Ingestion")
    print("=" * 40)
    store = open_store()
    print(f"Storage: {store.kind}")

    for folder in sys.argv[1:]:
        for pdf in sorted(Path(folder).glob("*.pdf")):
            result = add_pdf(store, pdf.read_bytes(), pdf.name, uploaded_by="cli")
            print(("✓ " if result["ok"] else "✗ ") + result["message"])

    retriever = build_retriever(store)
    print(f"\n✅ {len(store.list_documents(ACTIVE))} active SOPs, {len(retriever.chunks)} chunks indexed.")
