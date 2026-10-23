# prompts.py

SYSTEM_RULES = """You are a quiz maker for school and college students.
You write clear multiple choice questions (MCQs).
You must reply with JSON only. No extra words. No markdown."""


def build_quiz_prompt(topic, material, num_questions, difficulty):
    """Make the full prompt for the AI."""

    if difficulty == "mixed":
        difficulty_rule = "Use a mix of difficulty: some easy, some medium, some hard."
    else:
        difficulty_rule = f'Every question must have difficulty "{difficulty}".'

    if material:
        source_rule = (
            "Use ONLY the study material below. "
            "Do not use outside facts.\n\n"
            f"STUDY MATERIAL:\n{material}"
        )
    else:
        source_rule = f"Make the questions from this topic: {topic}"

    return f"""{SYSTEM_RULES}

Make exactly {num_questions} MCQs.
{difficulty_rule}

Rules:
1. Each question has exactly 4 options: A, B, C, D.
2. Exactly one option is correct.
3. Wrong options must look possible, but must be clearly wrong.
4. "correct_answer" must be one letter: A, B, C or D.
5. "explanation" is 1 or 2 simple sentences: why the answer is right.
6. "difficulty" must be "easy", "medium" or "hard".
7. "topic_tag" is a short 1-3 word label for the sub-topic.
8. Do not repeat questions.

{source_rule}

Reply in this exact JSON shape:
{{
  "questions": [
    {{
      "question": "...",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_answer": "B",
      "explanation": "...",
      "difficulty": "easy",
      "topic_tag": "..."
    }}
  ]
}}"""