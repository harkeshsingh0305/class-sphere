from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field
from predictor import predict_students, THRESHOLD

app = FastAPI(
    title="ClassSphere At-Risk Student API",
    description="Send student activity data from the first 90 days, get back the risk of failing or withdrawing.",
    version="1.0.0",
)


class StudentData(BaseModel):
    """The 6 inputs the model was trained on. All values cover the first 90 days of the course.
    (Any extra fields sent by the backend, such as gender, region or total_clicks, are ignored.)"""

    num_assessments_done: int = Field(0, ge=0, description="Assessments submitted (up to day 90)")
    avg_score: float = Field(0, ge=0, le=100, description="Average score (0 if none)")
    min_score: float = Field(0, ge=0, le=100, description="Lowest score (0 if none)")
    weighted_score: float = Field(0, ge=0, description="Sum of score x weight / 100 (0 if none)")
    late_submissions: int = Field(0, ge=0, description="Assessments submitted late")
    active_days: int = Field(0, ge=0, description="Number of different days the student was active")


class PredictionResult(BaseModel):
    at_risk: bool              # True = student needs attention
    risk_probability: float    # 0 to 1 (higher = more risk)
    risk_level: str            # "Low", "Medium" or "High"


@app.get("/")
def health_check():
    """Backend can call this to check that the API is running."""
    return {"status": "ok", "threshold": THRESHOLD}


@app.post("/predict", response_model=PredictionResult)
def predict_one(student: StudentData):
    """Predict the risk for ONE student."""
    return predict_students([student.model_dump()])[0]


@app.post("/predict-batch", response_model=List[PredictionResult])
def predict_many(students: List[StudentData]):
    """Predict the risk for MANY students (for example a whole class).
    The results come back in the same order as the students you sent."""
    return predict_students([s.model_dump() for s in students])
