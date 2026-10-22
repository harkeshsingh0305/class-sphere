
def summary_prompt(text):
    return f"""
    You are an expert study assistant.

    Summarize the following notes.

    Requirements:
    - Use simple English.
    - Include important concepts.
    - Use headings and bullet points.
    - Avoid unnecessary details.
    - Do not invent facts.
    - If information is missing, do not guess.

    Notes:
    {text}
    """


def flashcard_prompt(text):
    return f"""
    Create 5 question-answer flashcards
    from the following study notes.

    Return valid JSON only in this format:
    {{
      "flashcards": [
        {{
          "question": "Question here",
          "answer": "Answer here"
        }}
      ]
    }}

    Do not invent facts.

    Notes:
    {text}
    """
