# app_quiz.py
# Chainlit UI for Network Security Quiz Agent (QUIZ ONLY, separate from Q&A)

import chainlit as cl

from quiz_core import (
    generate_random_quiz,
    generate_topic_quiz,
    grade_quiz,
)
from run_quiz import save_report


def format_question(q) -> str:
    text = f"**Q{q.id} ({q.qtype.upper()})**\n\n{q.question_text}"
    if q.qtype == "mcq" and q.options:
        text += "\n\nOptions:\n" + "\n".join(q.options)
    if q.qtype == "tf":
        text += "\n\n*(Answer with `True` or `False`)*"
    return text


@cl.on_chat_start
async def start_chat():
    cl.user_session.set("state", "choose_mode")
    cl.user_session.set("quiz", None)
    cl.user_session.set("answers", {})
    cl.user_session.set("index", 0)

    await cl.Message(
        "Network Security Quiz – Local Only\n\n"
        "Each quiz has 5 questions:\n"
        "- 2 Multiple-Choice (MCQ)\n"
        "- 2 True/False (TF)\n"
        "- 1 Open-Ended (OPEN)\n\n"
        "Choose:\n"
        "1️⃣ Random Quiz  \n"
        "2️⃣ Topic Quiz\n\n"
        "Reply with `1` or `2`."
    ).send()


@cl.on_message
async def handle_message(msg: cl.Message):
    content = (msg.content or "").strip()
    state = cl.user_session.get("state")

    # ---------- MODE SELECTION ----------
    if state == "choose_mode":
        if content not in ("1", "2"):
            await cl.Message(" Reply ONLY with `1` or `2`.").send()
            return

        cl.user_session.set("mode", content)
        cl.user_session.set("num_mcq", 2)
        cl.user_session.set("num_tf", 2)
        cl.user_session.set("num_open", 1)

        if content == "2":
            cl.user_session.set("state", "choose_topic")
            await cl.Message("Enter topic (e.g. TLS, firewalls, VPN):").send()
            return

        await cl.Message(" Generating **Random Quiz** from local materials...").send()
        quiz = generate_random_quiz(2, 2, 1)
        cl.user_session.set("quiz", quiz)
        cl.user_session.set("answers", {})
        cl.user_session.set("index", 0)
        cl.user_session.set("state", "asking")

        await cl.Message(" Quiz ready! Let's begin.").send()
        first = quiz.questions[0]
        await cl.Message(format_question(first)).send()
        return

    # ---------- TOPIC SELECTION ----------
    if state == "choose_topic":
        topic = content
        await cl.Message(f" Generating **Topic Quiz** on `{topic}`...").send()

        quiz = generate_topic_quiz(topic, 2, 2, 1)
        cl.user_session.set("quiz", quiz)
        cl.user_session.set("answers", {})
        cl.user_session.set("index", 0)
        cl.user_session.set("state", "asking")

        await cl.Message(" Quiz ready! Let's begin.").send()
        first = quiz.questions[0]
        await cl.Message(format_question(first)).send()
        return

    # ---------- ASKING QUESTIONS ----------
    if state == "asking":
        quiz = cl.user_session.get("quiz")
        answers = cl.user_session.get("answers")
        index = cl.user_session.get("index", 0)

        current_q = quiz.questions[index]
        answers[current_q.id] = content
        cl.user_session.set("answers", answers)

        index += 1
        cl.user_session.set("index", index)

        if index < len(quiz.questions):
            next_q = quiz.questions[index]
            await cl.Message(format_question(next_q)).send()
            return

        # ---------- GRADING ----------
        await cl.Message(" Grading your quiz...").send()
        grade_info = grade_quiz(quiz, answers)

        await send_results(grade_info)

        cl.user_session.set("state", "done")
        return

    # ---------- DONE ----------
    await cl.Message(" Quiz already complete. Start **New Chat** for another quiz.").send()


async def send_results(grade_info):
    summary = (
        f"### 🧾 Quiz Summary\n"
        f"Score: **{grade_info['total_score']:.2f} / {grade_info['max_score']:.2f}**\n"
        f"Percentage: **{grade_info['percentage']:.1f}%**"
    )
    await cl.Message(summary).send()

    for res in grade_info["results"]:
        q = res["question"]
        ua = res["user_answer"] or "(no answer given)"

        exp = (q.explanation or "").strip()
        if not exp:
            exp = "See the cited local slides for explanation."

        lines = []
        lines.append(f"**Q{q.id}:** {q.question_text}")
        lines.append(f"- **Your answer:** `{ua}`")
        lines.append(f"- **Score:** {res['score']}/{res['max_score']}")
        lines.append(f"- **Comment:** {res['comment']}")
        lines.append(f"- **Correct:** {q.correct_answer}")
        lines.append(f"- **Explanation:** {exp}")

        if q.sources:
            src_list = "\n".join([f"  • {s}" for s in q.sources])
            lines.append(f"- **Local Sources:**\n{src_list}")

        await cl.Message("\n".join(lines)).send()

    save_report(grade_info)
    await cl.Message(
        "📄 Report saved under `reports/`.\n"
        "Click **New Chat** to take another quiz!"
    ).send()

