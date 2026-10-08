from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    technical_score: float
    communication_score: float
    relevance_score: float
    depth_score: float
    overall_score: float
    feedback: str