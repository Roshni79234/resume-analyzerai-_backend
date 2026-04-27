import time
from services.hf_api import query_llm

def generate_question(role, history):
    context = "\n".join(history)

    prompt = f"""
You are a professional interviewer for the role of {role}.

Conversation so far:
{context}

Ask the next interview question. Do NOT repeat.
"""

    res = query_llm(prompt)

    try:
        return res[0]["generated_text"]
    except:
        return "Tell me about yourself."


def evaluate_answer(question, answer, role):
    prompt = f"""
Evaluate this answer.

Role: {role}
Question: {question}
Answer: {answer}

Return:
Score: X/10
Feedback: short feedback
"""

    res = query_llm(prompt)

    try:
        return res[0]["generated_text"]
    except:
        return "Score: 5/10\nFeedback: Could not evaluate."


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