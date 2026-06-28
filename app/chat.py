import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from rag.vectorstore import load_vectorstore, vectorstore_exists
from rag.retriever import get_retriever
from rag.chain import build_rag_chain, query_chain


@st.cache_resource(show_spinner="Loading knowledge base...")
def initialize_chain(use_fallback: bool = False):
    if not vectorstore_exists():
        raise RuntimeError(
            "Vector store not found. Run `python ingest.py` first."
        )
    vectorstore = load_vectorstore()
    retriever = get_retriever(vectorstore)
    chain_tuple = build_rag_chain(retriever, use_fallback=use_fallback)
    return chain_tuple


def get_answer(question: str, use_fallback: bool = False) -> dict:
    chain_tuple = initialize_chain(use_fallback)
    return query_chain(chain_tuple, question)