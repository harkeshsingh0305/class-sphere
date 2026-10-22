

from pathlib import Path

import joblib
import pandas as pd

# The risk cut-off we chose in the notebook (chosen_threshold = 0.35)
THRESHOLD = 0.35

# STEP 1: Load the model ONE time when the server starts
MODEL_PATH = Path(__file__).parent / "best_model.pkl"
model = joblib.load(MODEL_PATH)

# The exact column names (and order) the model was trained with
MODEL_COLUMNS = list(model.feature_names_in_)

# These columns are text. In the notebook we used pd.get_dummies(drop_first=True),
# so each text value became its own 0/1 column, like "gender_M".
CATEGORY_COLUMNS = [
    "code_module", "code_presentation", "gender", "region",
    "highest_education", "imd_band", "age_band", "disability",
]


def build_row(student: dict) -> dict:
    """Change ONE student (a dictionary) into the 55 columns the model needs."""

    # Start with every model column = 0
    row = {col: 0 for col in MODEL_COLUMNS}

    # STEP 2: Fill the number columns (same names as in the notebook)
    number_columns = [
        "num_of_prev_attempts", "studied_credits", "date_registration",
        "num_assessments_done", "avg_score", "min_score", "weighted_score",
        "late_submissions", "total_clicks", "active_days",
        "resources_visited", "clicks_last_30_days",
    ]
    for col in number_columns:
        row[col] = student[col]

    # STEP 3: Make the extra columns, same as the notebook
    unreg = student.get("date_unregistration")        # can be None
    row["has_unregistration"] = 0 if unreg is None else 1
    row["date_unregistration"] = 0 if unreg is None else unreg

    if student["active_days"] > 0:
        row["avg_clicks_per_day"] = student["total_clicks"] / student["active_days"]
    else:
        row["avg_clicks_per_day"] = 0

    row["no_assessment"] = 1 if student["num_assessments_done"] == 0 else 0

    # STEP 4: Turn text into 0/1 columns.
    # Example: gender = "M"  ->  row["gender_M"] = 1
    # If the column does not exist (like "gender_F"), it was dropped in
    # training, so we leave everything at 0. That is correct.
    for col in CATEGORY_COLUMNS:
        dummy_name = f"{col}_{student[col]}"
        if dummy_name in row:
            row[dummy_name] = 1

    return row


def risk_level(probability: float) -> str:
    """Simple label for the frontend. You can change these numbers."""
    if probability >= 0.65:
        return "High"
    if probability >= THRESHOLD:
        return "Medium"
    return "Low"


def predict_students(students: list) -> list:
    """Predict for one or many students. Always takes and returns a list."""

    rows = [build_row(s) for s in students]
    table = pd.DataFrame(rows, columns=MODEL_COLUMNS)   # keeps the right order

    # predict_proba gives [safe_chance, risk_chance]. We want the risk chance.
    probabilities = model.predict_proba(table)[:, 1]

    results = []
    for p in probabilities:
        p = float(p)
        results.append({
            "at_risk": p >= THRESHOLD,
            "risk_probability": round(p, 4),
            "risk_level": risk_level(p),
        })
    return results
