import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL = "llama-3.1-8b-instant"

SQLALCHEMY_DATABASE_URI="sqlite:///app.db"

SQLALCHEMY_TRACK_MODIFICATIONS=False

JWT_SECRET_KEY="secret123"