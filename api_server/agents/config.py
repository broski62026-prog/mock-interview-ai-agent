import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

groq_model = OpenAIChatCompletionsModel(
    model="qwen/qwen3.8-27b",
    openai_client=groq_client,
)