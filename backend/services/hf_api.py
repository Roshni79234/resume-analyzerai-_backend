import requests
import time
from config import HEADERS, HF_MODEL

API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

def query_llm(prompt):
    payload = {"inputs": prompt}

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    # 🔥 Handle non-JSON safely
    try:
        data = response.json()
    except:
        print("RAW RESPONSE:", response.text)
        return "Model not responding. Try again."

    print("HF RESPONSE:", data)

    # 🔁 Handle model loading
    if isinstance(data, dict) and "error" in data:
        if "loading" in data["error"].lower():
            time.sleep(2)
            return "Model is loading, please try again..."

        return f"Error: {data['error']}"

    return data