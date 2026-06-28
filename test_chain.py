from rag.vectorstore import load_vectorstore
from rag.retriever import get_retriever
from rag.chain import build_rag_chain, query_chain

vs = load_vectorstore()
r = get_retriever(vs)
chain_tuple = build_rag_chain(r)
result = query_chain(chain_tuple, "What PPE is required in the coke oven area?")
print("\nAnswer:")
print(result['answer'])
print("\nSources:")
print(result['sources'])