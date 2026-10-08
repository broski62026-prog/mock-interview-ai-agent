from fastapi import APIRouter, HTTPException

from api_server.schemas.answer import (
    AnswerRequest,
    AnswerResponse
)

from api_server.database.connection import get_db_connection


router = APIRouter(
    prefix="/answers",
    tags=["Answers"]
)


@router.post("/", response_model=AnswerResponse)
def submit_answer(data: AnswerRequest):

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check that the question exists
    cursor.execute(
        """
        SELECT
            id,
            interview_id,
            message_number
        FROM interviews_message
        WHERE id = %s
        AND role = 'interviewer'
        """,
        (data.question_id,)
    )

    question = cursor.fetchone()

    if not question:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    question_message_id = question[0]
    interview_id = question[1]
    question_number = question[2]

    # Check whether this question already has an answer
    cursor.execute(
        """
        SELECT id
        FROM interviews_message
        WHERE interview_id = %s
        AND role = 'user'
        AND message_number = %s
        """,
        (
            interview_id,
            question_number
        )
    )

    existing_answer = cursor.fetchone()

    if existing_answer:

        cursor.close()
        connection.close()

        return {
            "message": "Answer already saved",
            "interview_id": interview_id,
            "question_id": question_message_id,
            "message_id": existing_answer[0]
        }

    # Save user answer
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
            "user",
            data.answer,
            question_number,
            "answered" if data.answer.strip() else "skipped"
        )
    )

    message_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Answer saved successfully",
        "interview_id": interview_id,
        "question_id": question_message_id,
        "message_id": message_id
    }