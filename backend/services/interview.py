import time
from services.hf_api import query_llm

def generate_question(role, history):
    context = "\n".join(history)

    prompt = f"""
You are an interviewer for {role}.

Conversation:
{context}

Ask ONE clear interview question.
"""

    res = query_llm(prompt)

    # Handle different formats
    if isinstance(res, str):
        return res

    if isinstance(res, list):
        return res[0].get("generated_text", "No question generated")

    if isinstance(res, dict):
        if "generated_text" in res:
            return res["generated_text"]
        if "error" in res:
            return f"Model error: {res['error']}"

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

    if isinstance(res, list):
        return res[0].get("generated_text", "No evaluation")

    if isinstance(res, dict):
        if "generated_text" in res:
            return res["generated_text"]
        if "error" in res:
            return f"Model error: {res['error']}"

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