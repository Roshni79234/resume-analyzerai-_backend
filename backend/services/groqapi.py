import requests
from config import GROQ_API_KEY, GROQ_URL, MODEL

# 🔥 HEADERS (uses API key from config)
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}


def query_llm(prompt):
    payload = {
        "model": MODEL,  # e.g., "llama3-70b-8192"
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

        # ✅ Success
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]

        # ❌ API error
        return {"error": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}