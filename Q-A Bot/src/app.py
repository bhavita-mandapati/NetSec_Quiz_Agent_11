import os, traceback
import chainlit as cl
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSIST_DIR = os.environ.get("PERSIST_DIR", "db")
TOP_K = int(os.environ.get("TOP_K", "4"))

def get_retriever():
    vs = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    )
    return vs.as_retriever(search_kwargs={"k": TOP_K})

@cl.on_message
async def main(message: cl.Message):
    try:
        q = message.content.strip()
        retriever = get_retriever()
        # LC 0.2+ uses .invoke(query)
        docs = retriever.invoke(q)

        parts = []
        cites = []
        for i, d in enumerate(docs):
            text = (d.page_content or "").strip()
            if text:
                parts.append(f"- {text[:400]}...")
            meta = d.metadata or {}
            fn = Path(meta.get("source","local")).name
            page = meta.get("page", meta.get("chunk", i))
            cites.append(f"{fn}:{page}")

        if not parts:
            await cl.Message(content="I couldn't find relevant local context. Try another question or re-run ingest.").send()
            return

        answer = "Here’s what I found locally:\n\n" + "\n\n".join(parts[:3]) + "\n\nCitations: " + ", ".join(dict.fromkeys(cites))[:1000]
        await cl.Message(content=answer).send()

    except Exception as e:
        err = f"Error:\n{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
        await cl.Message(content=err).send()

