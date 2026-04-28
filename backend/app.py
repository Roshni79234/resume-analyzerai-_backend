import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

from services.resume_analyzer import analyze_resume
from services.interview import (
    start_session,
    is_active,
    end_session,
    generate_question,
    evaluate_answer
)

# Load roles
with open("data/job_roles.json") as f:
    roles_data = json.load(f)

sessions = {}

@app.route("/")
def home():
    return "Backend running"

@app.route("/roles")
def roles():
    return jsonify(list(roles_data.keys()))

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json or {}

    resume = data.get("resume", "")
    role = data.get("role", "")

    if role not in roles_data:
        return jsonify({"error": "Invalid role"}), 400

    jd = roles_data[role]
    score = analyze_resume(resume, jd)

    return jsonify({
        "score": score,
        "suggestions": f"Improve skills relevant to {role}"
    })

@app.route("/start", methods=["POST"])
def start():
    data = request.json or {}

    user = data.get("user_id")
    role = data.get("role", "")
    duration = data.get("duration", 10)

    if not user:
        return jsonify({"error": "user_id required"}), 400

    session = start_session(duration)
    session["role"] = role

    sessions[user] = session

    q = generate_question(role, [])
    session["questions"].append(q)

    return jsonify({"question": q})

@app.route("/next", methods=["POST"])
def next_q():
    data = request.json or {}

    user = data.get("user_id")
    answer = data.get("answer", "")

    if user not in sessions:
        return jsonify({"error": "Session not found"}), 400

    session = sessions[user]

    if not is_active(session):
        return jsonify({"end": True, "result": end_session(session)})

    last_q = session["questions"][-1]

    eval_text = evaluate_answer(last_q, answer, session["role"])

    score = 5
    try:
        if "Score:" in eval_text:
            score = float(eval_text.split("Score:")[1].split("/")[0].strip())
    except:
        pass

    session["scores"].append(score)
    session["answers"].append(answer)
    session["history"].append(f"Q:{last_q} A:{answer}")

    q = generate_question(session["role"], session["history"])
    session["questions"].append(q)

    return jsonify({
        "question": q,
        "evaluation": eval_text,
        "score": score
    })

@app.route("/end", methods=["POST"])
def end():
    data = request.json or {}
    user = data.get("user_id")

    if user not in sessions:
        return jsonify({"error": "Session not found"}), 400

    return jsonify(end_session(sessions[user]))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    