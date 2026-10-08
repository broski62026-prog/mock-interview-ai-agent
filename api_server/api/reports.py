import json

from fastapi import APIRouter, HTTPException
from agents import Runner

from api_server.schemas.report import ReportResponse
from api_server.database.connection import get_db_connection
from api_server.agents.coach import coach_agent


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# -----------------------------------
# Get Existing Report
# -----------------------------------

@router.get(
    "/{interview_id}",
    response_model=ReportResponse
)
def get_report(interview_id: int):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            overall_score,
            strengths,
            weaknesses,
            recommendations,
            final_feedback
        FROM interviews_report
        WHERE interview_id = %s
        """,
        (interview_id,)
    )

    report = cursor.fetchone()

    cursor.close()
    connection.close()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return {
        "interview_id": interview_id,
        "overall_score": report[1],
        "strengths": report[2] or "",
        "weaknesses": report[3] or "",
        "recommendations": report[4] or "",
        "final_feedback": report[5] or ""
    }


# -----------------------------------
# End Interview and Generate Report
# -----------------------------------

@router.post(
    "/{interview_id}/end"
)
async def end_interview(interview_id: int):

    connection = get_db_connection()
    cursor = connection.cursor()

    # -----------------------------------
    # Check Interview
    # -----------------------------------

    cursor.execute(
        """
        SELECT
            id,
            status
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

    # -----------------------------------
    # Check Existing Report
    # -----------------------------------

    cursor.execute(
        """
        SELECT
            id
        FROM interviews_report
        WHERE interview_id = %s
        """,
        (interview_id,)
    )

    existing_report = cursor.fetchone()

    if existing_report:

        cursor.close()
        connection.close()

        return {
            "message": "Interview already ended",
            "interview_id": interview_id,
            "report_created": True
        }

    # -----------------------------------
    # Get Evaluations
    # -----------------------------------

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

    # -----------------------------------
    # Check Evaluations
    # -----------------------------------

    if not evaluations:

        cursor.execute(
            """
            UPDATE interviews_interview
            SET
                status = 'completed',
                ended_at = NOW()
            WHERE id = %s
            """,
            (interview_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return {
            "message": "Interview ended without evaluations",
            "interview_id": interview_id,
            "report_created": False
        }

    # -----------------------------------
    # Prepare Evaluations for Coach
    # -----------------------------------

    evaluations_text = ""

    for index, evaluation in enumerate(
        evaluations,
        start=1
    ):

        evaluations_text += f"""
Question {index} Evaluation:

Technical Score:
{evaluation[0]}

Communication Score:
{evaluation[1]}

Relevance Score:
{evaluation[2]}

Depth Score:
{evaluation[3]}

Overall Score:
{evaluation[4]}

Strengths:
{evaluation[5] or ""}

Weaknesses:
{evaluation[6] or ""}

Feedback:
{evaluation[7] or ""}

-------------------------
"""

    # -----------------------------------
    # Coach Agent
    # -----------------------------------

    coach_prompt = f"""
You are creating a final interview report.

The user ended the interview before completing all questions.

Use ONLY the evaluations that are available below.

Do not assume that unanswered questions were answered.

Create a final report based on the completed evaluations.

{evaluations_text}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "overall_score": 0,
    "strengths": "",
    "weaknesses": "",
    "recommendations": "",
    "final_feedback": ""
}}
"""

    coach_result = await Runner.run(
        coach_agent,
        coach_prompt
    )

    try:

        report_data = json.loads(
            coach_result.final_output
        )

    except json.JSONDecodeError:

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=500,
            detail="Coach Agent returned invalid JSON"
        )

    # -----------------------------------
    # Create Report
    # -----------------------------------

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
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW()
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

    # -----------------------------------
    # Mark Interview Completed
    # -----------------------------------

    cursor.execute(
        """
        UPDATE interviews_interview
        SET
            status = 'completed',
            ended_at = NOW()
        WHERE id = %s
        """,
        (interview_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Interview ended successfully",
        "interview_id": interview_id,
        "report_created": True,
        "report": report_data
    }