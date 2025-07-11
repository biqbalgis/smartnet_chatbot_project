import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variable
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load the Gemini 1.5 Flash model
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_response(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"





    

