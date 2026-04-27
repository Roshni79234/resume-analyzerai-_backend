import requests
import time
from config import HEADERS, HF_MODEL

API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

import requests
import time
from config import HEADERS, HF_MODEL

API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

def query_llm(prompt):
    payload = {"inputs": prompt}

    for i in range(3):  # 🔁 retry 3 times
        response = requests.post(API_URL, headers=HEADERS, json=payload)

        try:
            data = response.json()
        except:
            print("Attempt failed, retrying...")
            time.sleep(2)
            continue

        print("HF RESPONSE:", data)

        if isinstance(data, dict) and "error" in data:
            if "loading" in data["error"].lower():
                time.sleep(2)
                continue
            return data["error"]

        return data

    return "Model busy, please try again."