# run_quiz.py
# 5 questions per quiz

from typing import Dict
from datetime import datetime
import os

from quiz_core import (
    generate_random_quiz,
    generate_topic_quiz,
    grade_quiz,
)


def ask_user_for_answers(quiz) -> Dict[int, str]:
    answers = {}
    print("\n===== QUIZ START =====\n")

    for q in quiz.questions:
        print(f"\nQ{q.id} ({q.qtype.upper()}): {q.question_text}")
        if q.qtype == "mcq" and q.options:
            for opt in q.options:
                print(f"  {opt}")
        elif q.qtype == "tf":
            print("  (Answer with True or False)")

        user_ans = input("Your answer: ").strip()
        answers[q.id] = user_ans

    print("\n===== QUIZ COMPLETE =====\n")
    return answers


def save_report(grade_info):
    """
    Save an HTML report with all questions, answers, scores, and LOCAL citations only.
    You can open this in a browser or print to PDF.
    """
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/quiz_report_{timestamp}.html"

    html_parts = []
    html_parts.append("<html><head><meta charset='utf-8'>")
    html_parts.append("<title>Network Security Quiz Report</title>")
    html_parts.append(
        "<style>body{font-family:sans-serif;margin:20px;} "
        "h1{color:#333;} table{border-collapse:collapse;width:100%;} "
        "th,td{border:1px solid #ccc;padding:8px;vertical-align:top;} "
        "th{background:#f0f0f0;} .correct{color:green;} .incorrect{color:red;}</style>"
    )
    html_parts.append("</head><body>")

    html_parts.append("<h1>Network Security Quiz Report</h1>")
    html_parts.append(
        f"<p><b>Score:</b> {grade_info['total_score']:.2f}/"
        f"{grade_info['max_score']:.2f} ({grade_info['percentage']:.1f}%)</p>"
    )

    html_parts.append("<table>")
    html_parts.append(
        "<tr><th>#</th><th>Question</th><th>Your answer</th>"
        "<th>Score</th><th>Correct answer</th><th>Explanation</th>"
        "<th>Local sources</th></tr>"
    )

    for res in grade_info["results"]:
        q = res["question"]

        score_class = "correct" if res["score"] >= 1.0 else "incorrect"
        local_sources_html = "<br>".join(res["question"].sources)

        html_parts.append("<tr>")
        html_parts.append(f"<td>{q.id}</td>")
        html_parts.append(f"<td>{q.question_text}</td>")
        html_parts.append(f"<td>{res['user_answer']}</td>")
        html_parts.append(
            f"<td class='{score_class}'>{res['score']}/{res['max_score']}</td>"
        )
        html_parts.append(f"<td>{q.correct_answer}</td>")
        html_parts.append(f"<td>{q.explanation}</td>")
        html_parts.append(f"<td>{local_sources_html}</td>")
        html_parts.append("</tr>")

    html_parts.append("</table>")
    html_parts.append("</body></html>")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    print(f"\nHTML report saved to: {filename}")
    print("(Local-only: no internet sources used.)\n")


def main():
    print(" Network Security Quiz")
    print(" 5 questions per quiz, mixed types.\n")
    print("[1] Random quiz (mixed topics, 5 questions)")
    print("[2] Topic-based quiz (focus on one area, 5 questions)\n")

    mode = input("Enter 1 or 2: ").strip()

    # 5 questions each: 2 MCQ, 2 TF, 1 Open
    num_mcq = 2
    num_tf = 2
    num_open = 1

    if mode == "1":
        quiz = generate_random_quiz(
            num_mcq=num_mcq,
            num_tf=num_tf,
            num_open=num_open,
        )
    elif mode == "2":
        topic = input("Enter topic (e.g. 'TLS', 'firewalls', 'VPN'): ").strip()
        quiz = generate_topic_quiz(
            topic,
            num_mcq=num_mcq,
            num_tf=num_tf,
            num_open=num_open,
        )
    else:
        print("Invalid mode. Exiting.")
        return

    user_answers = ask_user_for_answers(quiz)
    grade_info = grade_quiz(quiz, user_answers)

    print("===== QUIZ FEEDBACK =====\n")
    print(f"Total score: {grade_info['total_score']:.2f}/{grade_info['max_score']:.2f}")
    print(f"Percentage: {grade_info['percentage']:.1f}%\n")

    for res in grade_info["results"]:
        q = res["question"]
        print(f"Q{q.id}: {q.question_text}")
        print(f"Your answer: {res['user_answer']}")
        print(f"Score: {res['score']}/{res['max_score']}")
        print(f"Comment: {res['comment']}")
        print(f"Correct answer: {q.correct_answer}")
        print(f"Explanation: {q.explanation}")
        print("Sources (local course material):")
        for s in q.sources:
            print(f"  - {s}")
        print("-" * 40)

    save_report(grade_info)


if __name__ == "__main__":
    main()

