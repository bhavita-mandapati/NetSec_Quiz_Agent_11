import sys
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def main(q):
    vs = Chroma(
        persist_directory="db",
        embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    )
    # New retriever API prefers .invoke(...) or use vectorstore.similarity_search
    docs = vs.similarity_search(q, k=4)
    print(f"Retrieved {len(docs)} docs:")
    for d in docs:
        meta = d.metadata or {}
        preview = (d.page_content or "").replace("\n", " ")[:120]
        print(meta, preview)

if __name__ == "__main__":
    main(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else "TLS handshake")

