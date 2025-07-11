import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key securely
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

MISTRAL_EMBEDDING_URL = "https://api.mistral.ai/v1/embeddings"

def get_mistral_embedding(text):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": text,
        "model": "mistral-embed",
    }

    response = requests.post(MISTRAL_EMBEDDING_URL, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["data"][0]["embedding"]
