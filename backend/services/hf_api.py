import requests
import time
from config import HEADERS, HF_MODEL

API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

def query_llm(prompt):
    payload = {"inputs": prompt}

    for i in range(5):  # 🔁 more retries
        try:
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json=payload,
                timeout=30
            )

            # 🚨 handle HTTP errors properly
            if response.status_code == 200:
                data = response.json()
                print("HF RESPONSE:", data)
                return data

            if response.status_code in [503, 429]:
                wait = 2 ** i  # exponential backoff
                print(f"Model busy (status {response.status_code}). Retrying in {wait}s...")
                time.sleep(wait)
                continue

            # other errors
            print("HF ERROR:", response.text)
            return {"error": response.text}

        except requests.exceptions.RequestException as e:
            print("Request failed:", str(e))
            time.sleep(2)

    return {"error": "Model busy after multiple retries. Try again later."}