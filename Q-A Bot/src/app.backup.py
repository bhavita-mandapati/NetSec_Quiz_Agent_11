import os, json, time, asyncio
import chainlit as cl
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
# Optional: llama-cpp fallback
try:
    from langchain_community.llms import LlamaCpp
except Exception:
    LlamaCpp = None

PERSIST_DIR = os.environ.get("PERSIST_DIR", "db")
TOP_K = int(os.environ.get("TOP_K", "4"))

def get_embeddings():
    # Local sentence-transformers
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_llm():
    # Local-first LLM
    provider = os.environ.get("LLM_PROVIDER", "ollama")
    if provider == "ollama":
        return Ollama(model=os.environ.get("LLM_MODEL", "llama3"))
    if provider == "llama-cpp" and LlamaCpp is not None:
        return LlamaCpp(model_path=os.environ.get("LLAMA_CPP_MODEL", "models/llama-7b.gguf"))
    # As a last resort (still local), fall back to simple template echo
    class Dummy:
        def __call__(self, prompt):
            return "LLM unavailable. Retrieved context:\n" + prompt[:1200]
    return Dummy()

def get_retriever():
    embeddings = get_embeddings()
    vs = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
    return vs.as_retriever(search_kwargs={"k": TOP_K})

ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """You are a strict, citation-first Network Security tutor.
Use only the provided context to answer. Cite sources like (filename:page or chunk).
If not answerable from context, say you don't have it locally.

Question: {question}

Context:
{context}

Answer with a concise explanation followed by a "Citations:" list.
""")

def synthesize_answer(llm, question, docs):
    context_parts = []
    cites = []
    for i, d in enumerate(docs):
        meta = d.metadata or {}
        fn = Path(meta.get("source", "local")).name
        page = meta.get("page", meta.get("chunk", i))
        context_parts.append(d.page_content)
        cites.append(f"{fn}:{page}")
    context = "\n\n---\n\n".join(context_parts)
    prompt = ANSWER_PROMPT.format(question=question, context=context)
    result = llm(prompt.to_string()) if hasattr(llm, "__call__") else llm.invoke(prompt.to_string())  # support both
    if isinstance(result, dict) and "content" in result:
        text = result["content"]
    else:
        text = str(result)
    # Append citations if not present
    if "Citations:" not in text:
        text += "\n\nCitations: " + ", ".join(list(dict.fromkeys(cites)))
    return text

@cl.on_message
async def main(message: cl.Message):
    question = message.content.strip()
    retriever = get_retriever()
    docs = retriever.get_relevant_documents(question)
    llm = get_llm()
    answer = synthesize_answer(llm, question, docs)
    await cl.Message(content=answer).send()
