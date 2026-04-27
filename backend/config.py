import os

HF_TOKEN = os.environ.get("HF_TOKEN")

HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}