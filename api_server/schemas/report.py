from pydantic import BaseModel


class ReportResponse(BaseModel):
    interview_id: int
    overall_score: float
    strengths: str
    weaknesses: str
    recommendations: str
    final_feedback: str