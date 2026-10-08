from pydantic import BaseModel


class AnswerRequest(BaseModel):
    interview_id: int
    question_id: int
    answer: str


class AnswerResponse(BaseModel):
    message: str
    interview_id: int
    question_id: int
    message_id: int