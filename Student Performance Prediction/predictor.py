from pathlib import Path
import joblib
import pandas as pd

# Decision threshold chosen in the notebook (`chosen_threshold = 0.35`).
# A lower threshold than 0.5 catches more at-risk students (recall ~0.75).
THRESHOLD = 0.35

# The 6 features the model was trained on, in the same order as the notebook's X.
# (No capping is applied: the notebook no longer clips any column.)
FEATURE_COLUMNS = [
    "num_assessments_done",
    "avg_score",
    "min_score",
    "weighted_score",
    "late_submissions",
    "active_days",
]

MODEL_PATH = Path(__file__).parent / "best_model.pkl"
model = joblib.load(MODEL_PATH)

# Safety check: fail at start-up (not at prediction time) if the model and this file disagree.
_model_columns = list(model.feature_names_in_)
if _model_columns != FEATURE_COLUMNS:
    raise RuntimeError(
        f"Feature mismatch.\nModel expects: {_model_columns}\nPredictor sends: {FEATURE_COLUMNS}"
    )


def build_row(student: dict) -> dict:
    """Pick the 6 columns the model needs from ONE student (a dictionary)."""
    return {col: student[col] for col in FEATURE_COLUMNS}


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
    table = pd.DataFrame(rows, columns=FEATURE_COLUMNS).astype(float)

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
