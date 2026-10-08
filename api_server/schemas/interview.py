from pydantic import BaseModel


class InterviewResponse(BaseModel):
    interview_id: int
    message: str