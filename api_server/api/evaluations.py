import json

from fastapi import APIRouter, HTTPException
from agents import Runner

from api_server.database.connection import get_db_connection
from api_server.agents.evaluator import evaluator_agent
from api_server.agents.coach import coach_agent


router = APIRouter(
    prefix="/evaluations",
    tags=["Evaluations"]
)


@router.post("/{answer_message_id}")
async def evaluate_answer(answer_message_id: int):

    connection = get_db_connection()
    cursor = connection.cursor()

    # Get answer
    cursor.execute(
        """
        SELECT
            interview_id,
            id,
            content,
            message_number
        FROM interviews_message
        WHERE id = %s
        AND role = 'user'
        """,
        (answer_message_id,)
    )

    answer = cursor.fetchone()

    if not answer:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Answer not found"
        )

    interview_id = answer[0]
    message_id = answer[1]
    answer_text = answer[2]
    question_number = answer[3]

    # Check whether answer is already evaluated
    cursor.execute(
        """
        SELECT id
        FROM interviews_evaluation
        WHERE answer_message_id = %s
        """,
        (message_id,)
    )

    existing_evaluation = cursor.fetchone()

    if existing_evaluation:

        cursor.close()
        connection.close()

        return {
            "message": "Answer already evaluated",
            "evaluation_id": existing_evaluation[0],
            "answer_message_id": message_id,
            "question_number": question_number
        }

    # Get the exact question for this answer
    cursor.execute(
        """
        SELECT content
        FROM interviews_message
        WHERE interview_id = %s
        AND role = 'interviewer'
        AND message_number = %s
        """,
        (
            interview_id,
            question_number
        )
    )

    question = cursor.fetchone()

    question_text = (
        question[0]
        if question
        else "No question available"
    )

    prompt = f"""
    Evaluate this interview answer.

    Question:
    {question_text}

    User Answer:
    {answer_text}

    Evaluate the answer on:

    1. Technical Knowledge: score 0-10
    2. Communication: score 0-10
    3. Relevance: score 0-10
    4. Depth: score 0-10

    Calculate overall_score as the average.

    Also provide:
    - Strengths
    - Weaknesses
    - Feedback

    Return ONLY valid JSON.
    """

    result = await Runner.run(
        evaluator_agent,
        prompt
    )

    evaluation_data = json.loads(
        result.final_output
    )

    # Save evaluation
    cursor.execute(
        """
        INSERT INTO interviews_evaluation
        (
            interview_id,
            answer_message_id,
            technical_score,
            communication_score,
            relevance_score,
            depth_score,
            overall_score,
            strengths,
            weaknesses,
            feedback,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        RETURNING id
        """,
        (
            interview_id,
            message_id,
            evaluation_data["technical_score"],
            evaluation_data["communication_score"],
            evaluation_data["relevance_score"],
            evaluation_data["depth_score"],
            evaluation_data["overall_score"],
            evaluation_data["strengths"],
            evaluation_data["weaknesses"],
            evaluation_data["feedback"]
        )
    )

    evaluation_id = cursor.fetchone()[0]

    # Get total question count for this interview
    cursor.execute(
        """
        SELECT question_count
        FROM interviews_interview
        WHERE id = %s
        """,
        (interview_id,)
    )

    interview = cursor.fetchone()

    if not interview:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    total_questions = interview[0]

    # Check whether all questions are completed
    interview_completed = (
        question_number >= total_questions
    )

    report_created = False

    if interview_completed:

        # Get all evaluations for this interview
        cursor.execute(
            """
            SELECT
                technical_score,
                communication_score,
                relevance_score,
                depth_score,
                overall_score,
                strengths,
                weaknesses,
                feedback
            FROM interviews_evaluation
            WHERE interview_id = %s
            ORDER BY id
            """,
            (interview_id,)
        )

        evaluations = cursor.fetchall()

        evaluations_text = ""

        for index, evaluation in enumerate(
            evaluations,
            start=1
        ):
            evaluations_text += f"""
            Question {index} Evaluation:

            Technical Score: {evaluation[0]}
            Communication Score: {evaluation[1]}
            Relevance Score: {evaluation[2]}
            Depth Score: {evaluation[3]}
            Overall Score: {evaluation[4]}

            Strengths:
            {evaluation[5]}

            Weaknesses:
            {evaluation[6]}

            Feedback:
            {evaluation[7]}

            -------------------------
            """

        # Ask Coach Agent for final report
        coach_prompt = f"""
        Analyze the following interview evaluations.

        {evaluations_text}

        Create the candidate's final interview report.

        Consider all evaluations from this interview together.

        Return ONLY valid JSON.
        """

        coach_result = await Runner.run(
            coach_agent,
            coach_prompt
        )

        report_data = json.loads(
            coach_result.final_output
        )

        # Check whether report already exists
        cursor.execute(
            """
            SELECT id
            FROM interviews_report
            WHERE interview_id = %s
            """,
            (interview_id,)
        )

        existing_report = cursor.fetchone()

        if not existing_report:

            # Save final report
            cursor.execute(
                """
                INSERT INTO interviews_report
                (
                    interview_id,
                    overall_score,
                    strengths,
                    weaknesses,
                    recommendations,
                    final_feedback,
                    created_at
                )
                VALUES
                (
                    %s, %s, %s, %s, %s, %s, NOW()
                )
                """,
                (
                    interview_id,
                    report_data["overall_score"],
                    report_data["strengths"],
                    report_data["weaknesses"],
                    report_data["recommendations"],
                    report_data["final_feedback"]
                )
            )

            report_created = True

        else:
            report_created = True

        # Mark interview completed
        cursor.execute(
            """
            UPDATE interviews_interview
            SET status = 'completed',
                ended_at = NOW()
            WHERE id = %s
            """,
            (interview_id,)
        )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "AI evaluation created successfully",
        "evaluation_id": evaluation_id,
        "answer_message_id": message_id,
        "question_number": question_number,
        "interview_completed": interview_completed,
        "report_created": report_created,
        "evaluation": evaluation_data
    }