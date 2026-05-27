import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from models.user import db, User
from models.interview_model import Interview

app = Flask(__name__)
CORS(app)

# ================= DB CONFIG =================

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set in environment variables")

# Fix for Render PostgreSQL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ================= JWT CONFIG =================

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret")

# ================= INIT EXTENSIONS =================

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ================= CREATE TABLES =================

with app.app_context():
    db.create_all()

# ================= IMPORT SERVICES =================

from services.resume_analyzer import analyze_resume
from services.interview import (
    start_session,
    is_active,
    end_session,
    generate_question,
    evaluate_answer
)

# Load job roles
with open("data/job_roles.json") as f:
    roles_data = json.load(f)

sessions = {}

# ================= AUTH =================

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing fields"}), 400

    existing = User.query.filter_by(email=data["email"]).first()

    if existing:
        return jsonify({"error": "User already exists"}), 400

    hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = User(
        username=data.get("username"),
        email=data["email"],
        password=hashed
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registered successfully"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}

    user = User.query.filter_by(email=data.get("email")).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if bcrypt.check_password_hash(user.password, data.get("password")):
        # FIX: use user.id instead of email
        token = create_access_token(identity=user.id)

        return jsonify({"token": token})

    return jsonify({"error": "Wrong password"}), 401


@app.route("/profile")
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })


# ================= BASIC ROUTES =================

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


# ================= INTERVIEW SESSION =================

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
        return jsonify({
            "end": True,
            "result": end_session(session)
        })

    last_q = session["questions"][-1]

    eval_text = evaluate_answer(last_q, answer, session["role"])

    score = 5
    try:
        if "Score:" in eval_text:
            score = float(
                eval_text.split("Score:")[1].split("/")[0].strip()
            )
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

    result = end_session(sessions[user])

    record = Interview(
        username=str(user),
        role=sessions[user]["role"],
        score=result["final_score"],
        feedback=str(result)
    )

    db.session.add(record)
    db.session.commit()

    return jsonify(result)


# ================= RUN =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )