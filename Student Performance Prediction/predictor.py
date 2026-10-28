from pathlib import Path
import joblib
import pandas as pd

THRESHOLD = 0.45

MODEL_PATH = Path(__file__).parent / "best_model.pkl"
model = joblib.load(MODEL_PATH)

MODEL_COLUMNS = list(model.feature_names_in_)

CATEGORY_COLUMNS = [
    "code_module", "code_presentation", "gender", "region",
    "highest_education", "imd_band", "age_band", "disability",
]

def build_row(student: dict) -> dict:
    """Change ONE student (a dictionary) into the 55 columns the model needs."""
   
    row = {col: 0 for col in MODEL_COLUMNS}
   
    number_columns = [
        "num_of_prev_attempts", "studied_credits", "date_registration",
        "num_assessments_done", "avg_score", "min_score", "weighted_score",
        "late_submissions", "total_clicks", "active_days",
        "resources_visited", "clicks_last_30_days",
    ]
    for col in number_columns:
        row[col] = student[col]

    if student["active_days"] > 0:
        row["avg_clicks_per_day"] = student["total_clicks"] / student["active_days"]
    else:
        row["avg_clicks_per_day"] = 0

    row["no_assessment"] = 1 if student["num_assessments_done"] == 0 else 0

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
    table = pd.DataFrame(rows, columns=MODEL_COLUMNS)  

  
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
