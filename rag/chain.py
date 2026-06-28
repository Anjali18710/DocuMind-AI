"""
chain.py
--------
Builds the RAG chain using LangChain.
Primary LLM: Groq (llama3-8b-8192)
Fallback LLM: Gemini (gemini-1.5-flash)
"""

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema.retriever import BaseRetriever
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import (
    GROQ_API_KEY, GEMINI_API_KEY,
    GROQ_MODEL, GEMINI_MODEL, PRIMARY_LLM
)

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert assistant for SAIL Bokaro Steel Plant.
Answer questions about SOPs and safety guidelines using ONLY the context below.

Rules:
- Answer strictly from the context provided.
- If the answer is not in the context, say: "I could not find this information in the available documents. Please consult the relevant department."
- Always mention which document the information comes from.
- Be concise and precise.
- For safety-critical procedures, always remind workers to follow official protocols.

Context:
{context}

Question: {question}

Answer:"""
)


def get_llm(use_fallback: bool = False):
    """Returns Groq (primary) or Gemini (fallback) LLM."""
    if not use_fallback and PRIMARY_LLM == "groq":
        print("✓ Using Groq LLM (primary)")
        return ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=0.1,
            max_tokens=1024,
        )
    else:
        print("✓ Using Gemini LLM (fallback)")
        return ChatGoogleGenerativeAI(
            google_api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
            temperature=0.1,
            max_output_tokens=1024,
        )


def build_rag_chain(retriever: BaseRetriever, use_fallback: bool = False) -> RetrievalQA:
    """Builds and returns the full RAG chain."""
    print(f"\n── Building RAG Chain ──────────────────")
    llm = get_llm(use_fallback)

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": RAG_PROMPT},
    )
    print("✓ RAG chain ready")
    return chain


def query_chain(chain: RetrievalQA, question: str) -> dict:
    """
    Runs a query through the RAG chain.
    Returns: { "answer": str, "sources": list[str] }
    """
    result = chain.invoke({"query": question})
    answer = result["result"]
    source_docs = result.get("source_documents", [])

    sources = list({
        doc.metadata.get("source", "Unknown")
        for doc in source_docs
    })

    return {
        "answer": answer,
        "sources": sources,
        "source_docs": source_docs,
    }