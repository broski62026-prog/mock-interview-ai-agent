from fastapi import FastAPI
from api_server.api.interviews import router as interview_router
from api_server.api.answers import router as answer_router
from api_server.api.reports import router as report_router
from api_server.api.evaluations import router as evaluation_router

app = FastAPI()


app.include_router(interview_router)
app.include_router(answer_router)
app.include_router(report_router)
app.include_router(evaluation_router)


@app.get("/")
def home():
    return {
        "message": "Mock Interview FastAPI is running"
    }