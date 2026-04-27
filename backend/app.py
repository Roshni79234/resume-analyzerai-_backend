import os, json
from flask import Flask, request, jsonify
from services.resume_analyzer import analyze_resume
from services.interview import *

app = Flask(__name__)

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
    data = request.json
    resume = data["resume"]
    role = data["role"]

    jd = roles_data[role]

    score = analyze_resume(resume, jd)

    return jsonify({
        "score": score,
        "suggestions": "Improve skills relevant to " + role
    })

@app.route("/start", methods=["POST"])
def start():
    data = request.json
    user = data["user_id"]
    role = data["role"]
    duration = data["duration"]

    session = start_session(duration)
    session["role"] = role

    sessions[user] = session

    q = generate_question(role, [])
    session["questions"].append(q)

    return jsonify({"question": q})

@app.route("/next", methods=["POST"])
def next_q():
    data = request.json
    user = data["user_id"]
    answer = data["answer"]

    session = sessions[user]

    if not is_active(session):
        return jsonify({"end": True, "result": end_session(session)})

    last_q = session["questions"][-1]

    eval_text = evaluate_answer(last_q, answer, session["role"])

    try:
        score = float(eval_text.split("Score:")[1].split("/")[0])
    except:
        score = 5

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
    user = request.json["user_id"]
    return jsonify(end_session(sessions[user]))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)