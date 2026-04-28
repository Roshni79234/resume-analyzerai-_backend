import time
from services.groqapi import query_llm


def generate_question(role, history):
    context = "\n".join(history)

    prompt = f"""
You are an interviewer for {role}.

Conversation so far:
{context}

Ask ONE clear interview question.
"""

    return query_llm(prompt)


def evaluate_answer(question, answer, role):
    prompt = f"""
You are an expert interviewer.

Question: {question}
Answer: {answer}
Role: {role}

Give:
Score out of 10
Short feedback
"""

    return query_llm(prompt)


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