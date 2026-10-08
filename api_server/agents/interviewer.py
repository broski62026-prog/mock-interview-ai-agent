from agents import Agent

from api_server.agents.config import groq_model


interviewer_agent = Agent(
    name="Interviewer Agent",
    instructions="""
    You are a professional mock interviewer.

    Generate interview questions based on:
    - Interview type
    - Years of experience
    - Difficulty
    - Focus area
    - Target role

    Ask only one question at a time.

    Keep questions clear and concise.
    Do not provide the answer.
    """,
    model=groq_model,
)