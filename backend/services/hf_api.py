import requests
import time
from threading import Lock
from config import HEADERS, HF_MODEL

API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

# Prevent multiple simultaneous requests (VERY IMPORTANT for Render)
hf_lock = Lock()


def query_llm(prompt):
    with hf_lock:  # ensures only 1 request at a time
        payload = {"inputs": prompt}

        for i in range(6):  # retry attempts
            try:
                response = requests.post(
                    API_URL,
                    headers=HEADERS,
                    json=payload,
                    timeout=30
                )

                # SUCCESS
                if response.status_code == 200:
                    try:
                        return response.json()
                    except:
                        return response.text

                # MODEL BUSY / RATE LIMIT
                if response.status_code in [503, 429]:
                    wait = min(2 ** i, 20)  # exponential backoff (max 20s)
                    print(f"HF busy ({response.status_code}). retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                # OTHER ERRORS
                print("HF ERROR:", response.text)
                return {"error": response.text}

            except requests.exceptions.RequestException as e:
                print("Request failed:", str(e))
                time.sleep(2)

        return {"error": "Model busy after multiple retries. Try again later."}