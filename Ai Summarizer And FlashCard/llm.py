import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import summary_prompt, flashcard_prompt

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Stop early with a clear message if the key is missing
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing in your .env file")

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.6-flash"

# Limit the text so very big PDFs do not break the model
MAX_CHARS = 30000


def generate_summary(text):
    text = text[:MAX_CHARS]

    response = client.models.generate_content(
        model=MODEL,
        contents=summary_prompt(text)
    )

    return response.text


def generate_flashcards(text):
    text = text[:MAX_CHARS]

    response = client.models.generate_content(
        model=MODEL,
        contents=flashcard_prompt(text),
        # This makes Gemini return pure JSON (no ```json marks)
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    result = json.loads(response.text)

    # Make sure we always return a dictionary
    if isinstance(result, list):
        result = {"flashcards": result}

    return result