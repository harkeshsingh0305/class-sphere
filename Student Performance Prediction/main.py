
from typing import List, Literal, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
from predictor import predict_students, THRESHOLD

app = FastAPI(
    title="ClassSphere At-Risk Student API",
    description="Send student activity data, get back the risk of failing or withdrawing.",
    version="1.0.0",
)


class StudentData(BaseModel):
 
    num_of_prev_attempts: int = Field(0, ge=0, description="Times the student tried this course before")
    studied_credits: int = Field(..., ge=0, description="Total credits the student is studying")
    date_registration: float = Field(..., description="Day the student registered (relative to course start, e.g. -45)")
    num_assessments_done: int = Field(0, ge=0, description="Assessments submitted")
    avg_score: float = Field(0, ge=0, le=100, description="Average score (0 if none)")
    min_score: float = Field(0, ge=0, le=100, description="Lowest score (0 if none)")
    weighted_score: float = Field(0, ge=0, description="Sum of score x weight / 100")
    late_submissions: int = Field(0, ge=0, description="Assessments submitted late")
    total_clicks: int = Field(0, ge=0, description="All clicks on the learning platform")
    active_days: int = Field(0, ge=0, description="Number of days the student was active")
    resources_visited: int = Field(0, ge=0, description="Different resources opened")
    clicks_last_30_days: int = Field(0, ge=0, description="Clicks in the last 30 days (days 61 to 90)")

 
    code_module: Literal["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"]
    code_presentation: Literal["2013B", "2013J", "2014B", "2014J"]
    gender: Literal["M", "F"]
    region: Literal[
        "East Anglian Region", "East Midlands Region", "Ireland", "London Region",
        "North Region", "North Western Region", "Scotland", "South East Region",
        "South Region", "South West Region", "Wales", "West Midlands Region",
        "Yorkshire Region",
    ]
    highest_education: Literal[
        "No Formal quals", "Lower Than A Level", "A Level or Equivalent",
        "HE Qualification", "Post Graduate Qualification",
    ]
    imd_band: Literal[
        "0-10", "10-20", "20-30", "30-40", "40-50",
        "50-60", "60-70", "70-80", "80-90", "90-100", "unknown",
    ]
    age_band: Literal["0-35", "35-55", "55<="]
    disability: Literal["Y", "N"]

    @field_validator("imd_band", mode="before")
    @classmethod
    def remove_percent_sign(cls, value):
        if isinstance(value, str):
            return value.replace("%", "")
        return value



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
