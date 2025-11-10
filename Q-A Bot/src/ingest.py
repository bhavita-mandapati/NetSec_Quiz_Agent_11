import os, argparse
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, UnstructuredPowerPointLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_docs(data_dir: str):
    data_path = Path(data_dir)
    docs = []
    # PDFs
    for pdf in list(data_path.glob("**/*.pdf")):
        loader = PyPDFLoader(str(pdf))
        docs.extend(loader.load())
    # PPTX
    for ppt in list(data_path.glob("**/*.pptx")):
        loader = UnstructuredPowerPointLoader(str(ppt))
        docs.extend(loader.load())
    return docs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", default="data")
    ap.add_argument("--persist_dir", default="db")
    ap.add_argument("--chunk_size", type=int, default=1000)
    ap.add_argument("--chunk_overlap", type=int, default=100)
    ap.add_argument("--max_docs", type=int, default=0, help="0 = all")
    args = ap.parse_args()

    docs = load_docs(args.data_dir)
    if args.max_docs and len(docs) > args.max_docs:
        docs = docs[:args.max_docs]

    splitter = RecursiveCharacterTextSplitter(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vs = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=args.persist_dir)
    vs.persist()
    print(f"Ingested {len(chunks)} chunks into {args.persist_dir}")

if __name__ == "__main__":
    main()
