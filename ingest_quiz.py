# ingest_quiz.py
# Build a local vector database for the Quiz Agent using files in data/

import os
from pathlib import Path

from tqdm import tqdm
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from config_quiz import (
    DATA_DIR,
    DB_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def load_docs_from_data_dir():
    docs = []
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        print(f"Data directory '{DATA_DIR}' does not exist.")
        return docs

    for path in data_path.glob("**/*"):
        if path.is_dir():
            continue
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            loader = PyPDFLoader(str(path))
        elif suffix in [".docx", ".doc"]:
            loader = Docx2txtLoader(str(path))
        elif suffix in [".pptx", ".ppt"]:
            loader = UnstructuredPowerPointLoader(str(path))
        else:
            print(f"Skipping unsupported file type: {path.name}")
            continue

        print(f"Loading {path}...")
        docs.extend(loader.load())
    return docs


def main():
    print("Loading documents from data/ ...")
    docs = load_docs_from_data_dir()
    if not docs:
        print("No documents found in data/. Add PDFs/PPTX/DOCX and try again.")
        return

    print(f"Loaded {len(docs)} documents. Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks.")

    print("Creating embeddings (this may take a while the first time)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    print("Building Chroma DB...")
    os.makedirs(DB_DIR, exist_ok=True)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR,
        collection_name=COLLECTION_NAME,
    )

    print("Done! Quiz vector DB created in 'db/'.")


if __name__ == "__main__":
    main()

