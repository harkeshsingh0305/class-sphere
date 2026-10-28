# llm.py
import json
import os
import time

from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "")  # optional backup model

# Wait this many seconds before each try: no wait, then 2s, then 4s
WAIT_BEFORE_TRY = [0, 2, 4]


class LLMError(Exception):
    """Raised when the AI call fails or returns bad JSON."""


def _clean_json_text(text):
    """Sometimes the AI adds ```json fences. Remove them."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return text.strip()


def _is_busy_error(error):
    """True if Google says: too busy or too many requests."""
    text = str(error)
    return "503" in text or "UNAVAILABLE" in text or "429" in text
def _ask_one_model(client, types, model_name, prompt):
    """Try one model up to 3 times. Return the text, or None if it was busy."""
    for wait_seconds in WAIT_BEFORE_TRY:
        if wait_seconds:
            time.sleep(wait_seconds)
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4,
                ),
            )
            return response.text
        except Exception as error:
            if _is_busy_error(error):
                continue              # busy: wait and try again
            raise LLMError(f"Gemini request failed: {error}")
    return None                       # still busy after 3 tries
def call_gemini(prompt):
    """Send the prompt to Gemini. Return the parsed JSON (dict)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMError("GEMINI_API_KEY is missing. Add it to your .env file.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    models_to_try = [MODEL_NAME]
    if FALLBACK_MODEL:
        models_to_try.append(FALLBACK_MODEL)

    raw_text = None
    for model_name in models_to_try:
        raw_text = _ask_one_model(client, types, model_name, prompt)
        if raw_text:
            break

    if not raw_text:
        raise LLMError("Gemini is busy right now. Please try again in a minute.")

    try:
        return json.loads(_clean_json_text(raw_text))
    except json.JSONDecodeError:
        raise LLMError("Gemini did not return valid JSON.")