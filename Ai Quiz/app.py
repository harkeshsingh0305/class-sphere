from flask import Flask, jsonify, request
from flask_cors import CORS
from generator import generate_quiz
from llm import LLMError
from pdf_utils import extract_text_from_pdf

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024

MAX_PDF_BYTES = 5 * 1024 * 1024
CORS(app)

@app.route("/",methods=["GET"])
def home():
    return {
        "message":"AI Quiz Generator API is running"
    },200

ALLOWED_LEVELS = ["easy", "medium", "hard", "mixed"]

def read_settings(source):
    """Read num_questions and difficulty. Return (num, level, error)."""
    try:
        num = int(source.get("num_questions", 5))
    except (TypeError, ValueError):
        return None, None, "num_questions must be a number"
    if not 1 <= num <= 20:
        return None, None, "num_questions must be between 1 and 20"

    level = str(source.get("difficulty", "mixed")).lower()
    if level not in ALLOWED_LEVELS:
        return None, None, "difficulty must be easy, medium, hard or mixed"
    return num, level, None


def run_generator(topic, material, num, level):
    try:
        result = generate_quiz(topic, material, num, level)
        return jsonify(result), 200
    except LLMError as error:
        return jsonify({"error": str(error)}), 502


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/generate-quiz")
def generate_from_text():
    body = request.get_json(silent=True) or {}
    topic = str(body.get("topic", "")).strip()
    material = str(body.get("study_material", "")).strip()

    if not topic and not material:
        return jsonify({"error": "Send 'topic' or 'study_material'."}), 400

    num, level, error = read_settings(body)
    if error:
        return jsonify({"error": error}), 400
    return run_generator(topic, material, num, level)


@app.post("/generate-quiz-from-pdf")
def generate_from_pdf():
    file = request.files.get("file")
    if file is None or not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Upload a PDF in the 'file' field."}), 400

    num, level, error = read_settings(request.form)
    if error:
        return jsonify({"error": error}), 400

    try:
        material = extract_text_from_pdf(file.read())
    except Exception:
        return jsonify({"error": "Could not read this PDF."}), 400
    if len(material) < 50:
        return jsonify({"error": "PDF has no readable text (scanned?)."}), 400

    return run_generator("", material, num, level)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

    