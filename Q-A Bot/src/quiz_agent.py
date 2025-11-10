from dataclasses import dataclass
from typing import List, Dict, Any
import random

@dataclass
class MCQ:
    question: str
    options: List[str]
    answer: str
    citations: List[str]

@dataclass
class TFQ:
    question: str
    answer: bool
    citations: List[str]

@dataclass
class OpenQ:
    question: str
    reference_answer: str
    citations: List[str]

def build_mcq_from_chunks(topic: str, chunks) -> MCQ:
    # Extremely simple heuristic stub – replace with LLM prompt synth if available
    base = chunks[0].page_content[:160].strip().replace("\n", " ")
    q = f"Which of the following best describes: {topic}?"
    opts = [base, "An unrelated concept", "A physical network cable", "A social engineering tactic"]
    random.shuffle(opts)
    return MCQ(q, opts, base, citations=_cite(chunks))

def build_tf_from_chunks(topic: str, chunks) -> TFQ:
    stmt = f"{topic} is part of the TLS handshake process."
    ans = True
    return TFQ(stmt, ans, citations=_cite(chunks))

def build_open_from_chunks(topic: str, chunks) -> OpenQ:
    ref = " ".join(c.page_content for c in chunks[:2])[:400]
    return OpenQ(f"Explain: {topic}", ref, citations=_cite(chunks))

def _cite(chunks):
    cites = []
    for i, d in enumerate(chunks):
        meta = d.metadata or {}
        fn = meta.get("source", "local").split("/")[-1]
        page = meta.get("page", meta.get("chunk", i))
        cites.append(f"{fn}:{page}")
    # de-dup and trim
    out = []
    for c in cites:
        if c not in out:
            out.append(c)
    return out[:5]
