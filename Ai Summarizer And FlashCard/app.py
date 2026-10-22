from flask import Flask, request, jsonify
from pdf_utils import extract_text
from llm import generate_summary, generate_flashcards
import tempfile
import os

app = Flask(__name__)

# Limit upload size to 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.route("/")
def home():
    return "AI Summarizer API is running!"


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "File is too large. Maximum is 10 MB."}), 413


@app.route("/summarize", methods=["POST"])
def summarize():
    file = request.files.get("file")

    if not file or not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF"}), 400

    path = None

    try:
        # Step 1: create the temp file and CLOSE it
        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False
        ) as temp:
            path = temp.name

        # Step 2: save the upload (works on Windows too)
        file.save(path)

        # Step 3: read the text, then always delete the temp file
        try:
            text = extract_text(path)
        finally:
            os.remove(path)

        if not text:
            return jsonify({
                "error": "No readable text found in PDF"
            }), 400

        # Step 4: ask Gemini
        summary = generate_summary(text)
        flashcards = generate_flashcards(text)

        return jsonify({
            "summary": summary,
            "flashcards": flashcards.get("flashcards", [])
        })

    except ValueError as error:
        # For example: password protected PDF
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Summarization failed")
        return jsonify({
            "error": "Unable to process PDF. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)