import asyncio

from agents import Runner

from api_server.agents.interviewer import interviewer_agent
from api_server.agents.evaluator import evaluator_agent


async def test_interviewer():

    result = await Runner.run(
        interviewer_agent,
        """
        Interview Type: Technical
        Years of Experience: 2
        Difficulty: Medium
        Focus Area: Python
        Target Role: Backend Developer

        Generate the first interview question.
        """
    )

    print("\n--- Interviewer Agent ---")
    print(result.final_output)


async def test_evaluator():

    result = await Runner.run(
        evaluator_agent,
        """
        Question:
        What is the difference between a list and a tuple in Python?

        User Answer:
        A list is mutable, while a tuple is immutable.
        Lists use square brackets and tuples use parentheses.
        """
    )

    print("\n--- Evaluator Agent ---")
    print(result.final_output)


async def main():

    await test_interviewer()
    await test_evaluator()


if __name__ == "__main__":
    asyncio.run(main())