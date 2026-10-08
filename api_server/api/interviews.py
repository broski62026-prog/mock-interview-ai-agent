from fastapi import APIRouter, HTTPException
from agents import Runner

from api_server.database.connection import get_db_connection
from api_server.agents.interviewer import interviewer_agent

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)


@router.get("/{interview_id}")
async def get_interview(interview_id: int):

    connection = get_db_connection()
    cursor = connection.cursor()

    # Get interview details
    cursor.execute(
        """
        SELECT
            id,
            interview_number,
            interview_type,
            years_of_experience,
            difficulty,
            focus_area,
            target_role,
            status,
            question_count
        FROM interviews_interview
        WHERE id = %s
        """,
        (interview_id,)
    )

    row = cursor.fetchone()

    if not row:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    interview_data = {
        "id": row[0],
        "interview_number": row[1],
        "interview_type": row[2],
        "years_of_experience": row[3],
        "difficulty": row[4],
        "focus_area": row[5],
        "target_role": row[6],
        "status": row[7],
        "question_count": row[8]
    }

    # Total questions configured for this interview
    total_questions = row[8]

    # Get all previous interviewer questions
    cursor.execute(
        """
        SELECT
            id,
            content,
            message_number
        FROM interviews_message
        WHERE interview_id = %s
        AND role = 'interviewer'
        ORDER BY message_number
        """,
        (interview_id,)
    )

    previous_questions = cursor.fetchall()

    # Number of questions already generated
    question_count = len(previous_questions)

    # Check whether all configured questions have been asked
    if question_count >= total_questions:

        cursor.execute(
            """
            UPDATE interviews_interview
            SET status = 'completed',
                ended_at = NOW()
            WHERE id = %s
            AND status = 'in_progress'
            """,
            (interview_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        interview_data["completed"] = True
        interview_data["question"] = None
        interview_data["question_number"] = total_questions

        return interview_data

    # Next question number
    next_question_number = question_count + 1

    # Prepare previous questions for the AI
    if previous_questions:

        previous_questions_text = "\n".join(
            f"- {question[1]}"
            for question in previous_questions
        )

    else:

        previous_questions_text = "None"

    # Generate next question
    prompt = f"""
    Generate interview question number {next_question_number}.

    Interview Type: {row[2]}
    Years of Experience: {row[3]}
    Difficulty: {row[4]}
    Focus Area: {row[5]}
    Target Role: {row[6]}

    This is question {next_question_number} of {total_questions}.

    Previous questions:
    {previous_questions_text}

    IMPORTANT RULES:

    1. Ask exactly ONE interview question.
    2. The new question MUST be different from all previous questions.
    3. Do NOT repeat a previous question.
    4. Do NOT rephrase a previous question.
    5. Test a different concept, skill, or aspect when possible.
    6. Keep the question clear and concise.
    7. Do not provide the answer.
    8. Do not provide explanation.
    """

    result = await Runner.run(
        interviewer_agent,
        prompt
    )

    question_text = result.final_output.strip()

    # Save interviewer question
    cursor.execute(
        """
        INSERT INTO interviews_message
        (
            interview_id,
            role,
            content,
            message_number,
            status,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING id
        """,
        (
            interview_id,
            "interviewer",
            question_text,
            next_question_number,
            "asked"
        )
    )

    question_message_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    interview_data["question"] = question_text
    interview_data["question_number"] = next_question_number
    interview_data["question_message_id"] = question_message_id
    interview_data["completed"] = False

    return interview_data