from rag.vectorstore import load_vectorstore
from rag.retriever import get_retriever

vs = load_vectorstore()
r = get_retriever(vs)
print("Invoking retriever...")
docs = r.invoke("What PPE is required?")
print(f"Got {len(docs)} docs")
for d in docs:
    print(d.page_content[:150])
    print("---")