# retrieval_quiz.py
# Helper to load the Quiz Agent's own vector database

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config_quiz import DB_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME


def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=DB_DIR,
    )
    return vectordb


def get_retriever(k: int = 5):
    vectordb = get_vectorstore()
    retriever = vectordb.as_retriever(search_kwargs={"k": k})
    return retriever

