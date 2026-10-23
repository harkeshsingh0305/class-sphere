# validator.py

LETTERS = ["A", "B", "C", "D"]
LEVELS = ["easy", "medium", "hard"]


def check_one_question(q):
    """Return (clean_question, None) if good, or (None, reason) if bad."""
    if not isinstance(q, dict):
        return None, "question is not an object"

    text = str(q.get("question", "")).strip()
    if len(text) < 10:
        return None, "question text is missing or too short"

    options = q.get("options")
    if not isinstance(options, dict):
        return None, "options is not an object"
    if sorted(options.keys()) != LETTERS:
        return None, "options must be exactly A, B, C, D"

    clean_options = {}
    for letter in LETTERS:
        value = str(options[letter]).strip()
        if not value:
            return None, f"option {letter} is empty"
        clean_options[letter] = value

    # No two options should be the same.
    lowered = [v.lower() for v in clean_options.values()]
    if len(set(lowered)) != 4:
        return None, "two options are the same"

    answer = str(q.get("correct_answer", "")).strip().upper()
    if answer not in LETTERS:
        return None, "correct_answer must be A, B, C or D"

    explanation = str(q.get("explanation", "")).strip()
    if not explanation:
        return None, "explanation is missing"

    difficulty = str(q.get("difficulty", "")).strip().lower()
    if difficulty not in LEVELS:
        return None, "difficulty must be easy, medium or hard"

    topic_tag = str(q.get("topic_tag", "")).strip() or "general"

    clean = {
        "question": text,
        "options": clean_options,
        "correct_answer": answer,
        "explanation": explanation,
        "difficulty": difficulty,
        "topic_tag": topic_tag,
    }
    return clean, None


def validate_questions(raw_questions):
    """Check a whole list. Return (good_list, problems_list)."""
    good = []
    problems = []
    seen_questions = set()

    if not isinstance(raw_questions, list):
        return [], ["'questions' is not a list"]

    for index, q in enumerate(raw_questions, start=1):
        clean, reason = check_one_question(q)
        if reason:
            problems.append(f"Question {index} dropped: {reason}")
            continue

        key = clean["question"].lower()
        if key in seen_questions:
            problems.append(f"Question {index} dropped: duplicate question")
            continue

        seen_questions.add(key)
        good.append(clean)

    return good, problems