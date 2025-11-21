# quiz_core.py
# Core logic for quiz generation & grading for the QUIZ AGENT

from dataclasses import dataclass
from typing import List, Optional, Literal, Dict, Any
import json
import random

from retrieval_quiz import get_retriever
from config_quiz import (
    DEFAULT_NUM_MCQ,
    DEFAULT_NUM_TF,
    DEFAULT_NUM_OPEN,
)

from langchain_community.chat_models import ChatOllama

QuestionType = Literal["mcq", "tf", "open"]


@dataclass
class Question:
    id: int
    qtype: QuestionType
    question_text: str
    options: Optional[List[str]]
    correct_answer: str
    explanation: str
    sources: List[str]


@dataclass
class Quiz:
    questions: List[Question]


# ============ LLM ============

def get_llm():
    """Ollama local model."""
    return ChatOllama(model="llama3")


# ============ RETRIEVAL HELPERS ============

def _docs_to_context(docs) -> (str, List[str]):
    parts: List[str] = []
    sources: List[str] = []

    for d in docs:
        text = d.page_content or ""
        if text:
            parts.append(text)

        meta = getattr(d, "metadata", {}) or {}
        src = meta.get("source")
        page = meta.get("page")
        if src:
            if page is not None:
                sources.append(f"{src}_page{page}")
            else:
                sources.append(str(src))

    seen = set()
    unique_sources: List[str] = []
    for s in sources:
        if s not in seen:
            seen.add(s)
            unique_sources.append(s)

    return "\n\n".join(parts), unique_sources


def _get_random_context(num_docs: int = 6) -> (str, List[str]):
    retriever = get_retriever(k=num_docs)
    queries = [
        "network security overview",
        "security services and mechanisms",
        "active and passive attacks",
        "OSI security architecture X.800",
        "CIA triad confidentiality integrity availability",
    ]
    q = random.choice(queries)
    docs = retriever.invoke(q)
    return _docs_to_context(docs)


def _get_topic_context(topic: str, k: int = 8) -> (str, List[str]):
    retriever = get_retriever(k=k)
    docs = retriever.invoke(topic)
    return _docs_to_context(docs)


# ============ QUIZ GENERATION ============

def _parse_quiz_json(text: str) -> List[Dict[str, Any]]:
    """
    Robust JSON extraction: find the first valid JSON object/array
    in the LLM output.
    """
    if not text:
        raise ValueError("Empty LLM response for quiz generation")

    decoder = json.JSONDecoder()
    s = text.strip()
    data = None

    for i in range(len(s)):
        ch = s[i]
        if ch not in ("{", "["):
            continue
        try:
            obj, end = decoder.raw_decode(s[i:])
            data = obj
            break
        except json.JSONDecodeError:
            continue

    if data is None:
        raise ValueError("No valid JSON found in LLM response")

    if isinstance(data, dict):
        if "questions" in data and isinstance(data["questions"], list):
            return data["questions"]
        if all(k in data for k in ("qtype", "question", "answer")):
            return [data]
        raise ValueError("JSON dict does not contain 'questions' list")

    if isinstance(data, list):
        return data

    raise ValueError("Unexpected JSON structure from LLM for quiz generation")


def _call_quiz_generation_llm(
    context: str,
    topic: Optional[str],
    num_mcq: int,
    num_tf: int,
    num_open: int,
) -> List[Dict[str, Any]]:
    llm = get_llm()
    topic_part = f"Focus on the topic: {topic}.\n" if topic else ""

    prompt = f"""
You are a helpful network security tutor.

{topic_part}
You are given the following local study materials (lecture slides, textbook excerpts, and quizzes):

\"\"\"{context}\"\"\"

From ONLY this material, generate exactly {num_mcq + num_tf + num_open} quiz questions
for a university-level network security course.

Use exactly this distribution:
- {num_mcq} multiple-choice (mcq)
- {num_tf} true/false (tf)
- {num_open} open-ended (open)

For each question, output:
- id: integer starting from 1
- qtype: "mcq", "tf", or "open"
- question: the question text
- options: for mcq only, a list like ["A. ...", "B. ...", "C. ...", "D. ..."]
- answer: the correct answer ("A"/"B"/"C"/"D" for mcq, "True"/"False" for tf, or short text for open)
- explanation: a brief explanation based strictly on the materials

Return ONLY valid JSON, in either format:
1)
{{
  "questions": [
    {{
      "id": 1,
      "qtype": "mcq",
      "question": "...",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "B",
      "explanation": "..."
    }},
    ...
  ]
}}

OR

2)
[
  {{
    "id": 1,
    "qtype": "mcq",
    "question": "...",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "B",
    "explanation": "..."
  }},
  ...
]
"""

    resp = llm.invoke(prompt)
    text = resp.content if hasattr(resp, "content") else str(resp)

    # 📌 DEBUG STEP 2: Print Raw LLM Response
    print("\n--- RAW LLM RESPONSE START ---\n")
    print(text)
    print("\n--- RAW LLM RESPONSE END ---\n")

    return _parse_quiz_json(text)



def _build_quiz_from_llm(
    question_dicts: List[Dict[str, Any]],
    sources: List[str],
) -> Quiz:
    questions: List[Question] = []

    for qd in question_dicts:
        try:
            # The error is caught here when trying to convert "5\"" to int
            qid = int(qd.get("id", len(questions) + 1))
            qtype_raw = (qd.get("qtype") or "").lower()
            if qtype_raw not in ("mcq", "tf", "open"):
                continue

            question_text = qd.get("question") or ""
            options = qd.get("options") if qtype_raw == "mcq" else None
            answer = qd.get("answer") or ""
            explanation = qd.get("explanation") or ""

            q = Question(
                id=qid,
                qtype=qtype_raw,  # type: ignore[arg-type]
                question_text=question_text,
                options=options,
                correct_answer=answer,
                explanation=explanation,
                sources=list(sources),
            )
            questions.append(q)
        except Exception as e:
            # THIS IS THE CRUCIAL DEBUGGING CHANGE:
            print(f"DEBUG: ❌ Skipping question due to parsing error: {e}")
            print(f"  Problematic Data: {qd.get('id', 'N/A')}. JSON: {qd}")
            continue

    return Quiz(questions=questions)

def generate_random_quiz(
    num_mcq: int = DEFAULT_NUM_MCQ,
    num_tf: int = DEFAULT_NUM_TF,
    num_open: int = DEFAULT_NUM_OPEN,
) -> Quiz:
    context, sources = _get_random_context()
    qdicts = _call_quiz_generation_llm(context, topic=None, num_mcq=num_mcq, num_tf=num_tf, num_open=num_open)
    return _build_quiz_from_llm(qdicts, sources)


def generate_topic_quiz(
    topic: str,
    num_mcq: int = DEFAULT_NUM_MCQ,
    num_tf: int = DEFAULT_NUM_TF,
    num_open: int = DEFAULT_NUM_OPEN,
) -> Quiz:
    context, sources = _get_topic_context(topic)
    qdicts = _call_quiz_generation_llm(context, topic=topic, num_mcq=num_mcq, num_tf=num_tf, num_open=num_open)
    return _build_quiz_from_llm(qdicts, sources)


# ============ GRADING ============

def grade_quiz(quiz: Quiz, user_answers: Dict[int, str]) -> Dict[str, Any]:
    """
    Grade the quiz using simple rules for MCQ/TF and
    token-overlap similarity for open-ended questions.
    Returns:
      {
        "total_score": float,
        "max_score": float,
        "percentage": float,
        "results": [
          {
            "question": Question,
            "user_answer": str,
            "score": float,
            "max_score": float,
            "comment": str,
          },
          ...
        ]
      }
    """
    results: List[Dict[str, Any]] = []
    total_score = 0.0
    max_score = 0.0

    for q in quiz.questions:
        user_answer = (user_answers.get(q.id) or "").strip()
        qtype = q.qtype
        q_correct = (q.correct_answer or "").strip()

        score = 0.0
        max_q_score = 1.0
        comment = ""

        # MCQ
        if qtype == "mcq":
            ua_norm = user_answer.strip().lower().replace(".", "")
            ca_norm = q_correct.strip().lower().replace(".", "")
            if ua_norm == ca_norm:
                score = 1.0
                comment = "Correct."
            elif not ua_norm:
                comment = "No answer given."
            else:
                comment = "Incorrect."

        # True/False
        elif qtype == "tf":
            ua_norm = user_answer.lower()
            ca_norm = q_correct.lower()
            if ua_norm in ("true", "t") and ca_norm == "true":
                score = 1.0
                comment = "Correct."
            elif ua_norm in ("false", "f") and ca_norm == "false":
                score = 1.0
                comment = "Correct."
            elif not ua_norm:
                comment = "No answer given."
            else:
                comment = "Incorrect."

        # Open-ended
        else:
            ua = user_answer.lower()
            ca = q_correct.lower()
            if not ua:
                comment = "No answer given."
            else:
                ua_tokens = set(ua.replace(",", " ").split())
                ca_tokens = set(ca.replace(",", " ").split())
                common = ua_tokens.intersection(ca_tokens)
                similarity = len(common) / len(ca_tokens) if ca_tokens else 0.0

                if similarity >= 0.9:
                    score = 1.0
                    comment = f"Very close to model answer (similarity {similarity:.2f})."
                elif similarity >= 0.5:
                    score = 0.5
                    comment = f"Partially correct (similarity {similarity:.2f})."
                else:
                    comment = f"Not very close to model answer (similarity {similarity:.2f})."

        results.append(
            {
                "question": q,
                "user_answer": user_answer,
                "score": score,
                "max_score": max_q_score,
                "comment": comment,
            }
        )

        total_score += score
        max_score += max_q_score

    percentage = (total_score / max_score * 100.0) if max_score > 0 else 0.0

    return {
        "total_score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "results": results,
    }
