import gradio as gr
import requests
import uuid

BACKEND = "https://your-render-url.onrender.com"
user_id = str(uuid.uuid4())

def get_roles():
    return requests.get(f"{BACKEND}/roles").json()

def analyze(resume, role):
    r = requests.post(f"{BACKEND}/analyze", json={
        "resume": resume,
        "role": role
    }).json()
    return r["score"], r["suggestions"]

def start(role, duration):
    r = requests.post(f"{BACKEND}/start", json={
        "user_id": user_id,
        "role": role,
        "duration": duration
    }).json()
    return r["question"]

def next_q(answer):
    r = requests.post(f"{BACKEND}/next", json={
        "user_id": user_id,
        "answer": answer
    }).json()

    if "end" in r:
        return "Interview Ended", r["result"]

    return r["question"], r["evaluation"]

with gr.Blocks() as demo:
    gr.Markdown("# Resume Analyzer + Interview Bot")

    role = gr.Dropdown(choices=get_roles(), label="Job Role")
    resume = gr.Textbox(label="Paste Resume")

    score = gr.Textbox(label="Score")
    suggestions = gr.Textbox(label="Suggestions")

    gr.Button("Analyze").click(analyze, [resume, role], [score, suggestions])

    gr.Markdown("## Interview")

    duration = gr.Dropdown([5,10,15], label="Duration")
    question = gr.Textbox(label="Question")
    answer = gr.Textbox(label="Answer")
    feedback = gr.Textbox(label="Feedback")

    gr.Button("Start").click(start, [role, duration], question)
    gr.Button("Next").click(next_q, answer, [question, feedback])

demo.launch()