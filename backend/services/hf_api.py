import requests
from config import HEADERS, HF_MODEL

API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

def query_llm(prompt):
    payload = {"inputs": prompt}

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    data = response.json()

    
    print("HF RESPONSE:", data)

    return data