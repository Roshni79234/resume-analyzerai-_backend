import time
from services.groqapi import query_llm


def generate_question(role, history):
    context = "\n".join(history)

    prompt = f"""
You are an interviewer for {role}.

Conversation:
{context}

Ask ONE clear interview question.
"""

    res = query_llm(prompt)

    # ✅ HANDLE STRING
    if isinstance(res, str):
        return res

    # ✅ HANDLE GROQ FORMAT
    if isinstance(res, dict):
        try:
            return res["choices"][0]["message"]["content"]
        except:
            return str(res)

    return "Could not generate question"


def evaluate_answer(question, answer, role):
    prompt = f"""
Evaluate this answer.

Question: {question}
Answer: {answer}

Give:
Score: X/10
Feedback: short feedback
"""

    res = query_llm(prompt)

    if isinstance(res, str):
        return res

    if isinstance(res, dict):
        try:
            return res["choices"][0]["message"]["content"]
        except:
            return str(res)

    return "Evaluation failed"


def start_session(duration):
    return {
        "start": time.time(),
        "duration": duration * 60,
        "history": [],
        "scores": [],
        "questions": [],
        "answers": []
    }


def is_active(session):
    return time.time() - session["start"] < session["duration"]


def end_session(session):
    if not session["scores"]:
        return {"final_score": 0}

    avg = sum(session["scores"]) / len(session["scores"])

    return {
        "final_score": round(avg, 2),
        "questions": session["questions"],
        "answers": session["answers"],
        "scores": session["scores"]
    }