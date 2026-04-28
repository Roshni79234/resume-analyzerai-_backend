import requests
from config import GROQ_API_KEY, GROQ_URL, HEADERS, MODEL


def query_llm(prompt):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            GROQ_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        return {"error": response.text}

    except Exception as e:
        return {"error": str(e)}