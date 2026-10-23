# generator.py
from llm import call_gemini, LLMError
from prompts import build_quiz_prompt
from validator import validate_questions

MAX_MATERIAL_CHARS = 12000  # keeps the prompt small
MAX_TRIES = 3


def generate_quiz(topic, material, num_questions, difficulty):
    material = (material or "").strip()[:MAX_MATERIAL_CHARS]
    topic = (topic or "").strip()

    all_good = []
    all_problems = []
    last_error = None

    for attempt in range(1, MAX_TRIES + 1):
        still_needed = num_questions - len(all_good)
        if still_needed <= 0:
            break

        prompt = build_quiz_prompt(topic, material, still_needed, difficulty)

        try:
            data = call_gemini(prompt)
        except LLMError as error:
            last_error = str(error)
            all_problems.append(f"Try {attempt}: {error}")
            continue

        good, problems = validate_questions(data.get("questions"))
        all_problems.extend(f"Try {attempt}: {p}" for p in problems)

        # Add only new questions (skip duplicates from earlier tries).
        known = {q["question"].lower() for q in all_good}
        for q in good:
            if q["question"].lower() not in known:
                all_good.append(q)
                known.add(q["question"].lower())

    if not all_good:
        raise LLMError(last_error or "No valid questions could be made.")

    all_good = all_good[:num_questions]
    for number, q in enumerate(all_good, start=1):
        q["id"] = number

    return {
        "topic": topic or "from study material",
        "requested": num_questions,
        "returned": len(all_good),
        "questions": all_good,
        "warnings": all_problems,
    }