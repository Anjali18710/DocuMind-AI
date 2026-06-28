"""
chain.py
--------
Builds the RAG chain using LangChain.
Primary LLM: Groq (llama-3.3-70b-versatile)
Fallback LLM: Gemini (gemini-1.5-flash)
"""

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import (
    GROQ_API_KEY, GEMINI_API_KEY,
    GROQ_MODEL, GEMINI_MODEL, PRIMARY_LLM
)

PROMPT_TEMPLATE = """You are an expert assistant for SAIL Bokaro Steel Plant.
Answer questions about SOPs and safety guidelines using ONLY the context below.

Rules:
- Answer strictly from the context provided.
- If the answer is not in the context, say: "I could not find this information in the available documents. Please consult the relevant department."
- Always mention which document the information comes from.
- Be concise and precise.

Context:
{context}

Question: {question}

Answer:"""


def get_llm(use_fallback: bool = False):
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


def build_rag_chain(retriever, use_fallback: bool = False):
    print(f"\n── Building RAG Chain ──────────────────")
    llm = get_llm(use_fallback)
    print("✓ RAG chain ready")
    return llm, retriever


def query_chain(chain_tuple, question: str) -> dict:
    llm, retriever = chain_tuple
    
    # Retrieve relevant docs
    source_docs = retriever.invoke(question)
    
    # Build context from docs
    context = "\n\n".join(doc.page_content for doc in source_docs)
    
    # Build prompt
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    
    # Call LLM directly
    response = llm.invoke(prompt)
    answer = response.content
    
    # Extract sources
    sources = list({
        doc.metadata.get("source", "Unknown")
        for doc in source_docs
    })
    
    return {
        "answer": answer,
        "sources": sources,
        "source_docs": source_docs,
    }