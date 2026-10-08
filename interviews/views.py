
import requests

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Interview


@login_required
def interview_setup_view(request):

    if request.method == "POST":

        years_of_experience = float(
            request.POST["years_of_experience"]
        )

        interview_type = request.POST["interview_type"]
        difficulty = request.POST["difficulty"]
        focus_area = request.POST.get("focus_area", "")
        target_role = request.POST["target_role"]

        # ---------------------------------
        # Question count based on difficulty
        # ---------------------------------

        if difficulty == "easy":
            question_count = 10

        elif difficulty == "medium":
            question_count = 7

        else:
            question_count = 5

        # ---------------------------------
        # Time settings
        # ---------------------------------

        # 2 minutes for every question
        question_time_limit = 120

        # Total interview duration
        duration_minutes = question_count * 2

        # ---------------------------------
        # Interview numbering
        # ---------------------------------

        last_interview = (
            Interview.objects.filter(
                user=request.user
            )
            .order_by("-interview_number")
            .first()
        )

        if last_interview:
            interview_number = (
                last_interview.interview_number + 1
            )
        else:
            interview_number = 1

        # ---------------------------------
        # Create interview
        # ---------------------------------

        interview = Interview.objects.create(
            user=request.user,
            interview_number=interview_number,
            interview_type=interview_type,
            years_of_experience=years_of_experience,
            difficulty=difficulty,
            focus_area=focus_area,
            target_role=target_role,
            duration_minutes=duration_minutes,
            question_time_limit=question_time_limit,
            question_count=question_count,
        )

        return redirect(
            "interview",
            interview_id=interview.id
        )

    return render(
        request,
        "interview_setup.html"
    )


@login_required
def interview_view(request, interview_id):

    interview = Interview.objects.get(
        id=interview_id,
        user=request.user
    )

    # -----------------------------
    # POST Requests
    # -----------------------------

    if request.method == "POST":

        # -----------------------------
        # End Interview
        # -----------------------------

        end_interview = (
            request.POST.get("end_interview") == "true"
        )

        if end_interview:

            response = requests.post(
                f"http://127.0.0.1:8001/reports/"
                f"{interview_id}/end"
            )

            if response.status_code == 200:

                return redirect(
                    "report",
                    interview_id=interview_id
                )

            return redirect(
                "interview",
                interview_id=interview_id
            )

        # -----------------------------
        # Submit Answer
        # -----------------------------

        answer = request.POST.get(
            "answer",
            ""
        ).strip()

        question_id = request.POST.get(
            "question_id"
        )

        if not question_id:
            return redirect(
                "interview",
                interview_id=interview_id
            )

        # Save answer
        answer_response = requests.post(
            "http://127.0.0.1:8001/answers/",
            json={
                "interview_id": interview_id,
                "question_id": int(question_id),
                "answer": answer,
            },
        )

        if answer_response.status_code != 200:
            return redirect(
                "interview",
                interview_id=interview_id
            )

        answer_data = answer_response.json()

        answer_message_id = (
            answer_data["message_id"]
        )

        # Evaluate answer
        evaluation_response = requests.post(
            f"http://127.0.0.1:8001/evaluations/"
            f"{answer_message_id}"
        )

        if evaluation_response.status_code == 200:

            evaluation_data = (
                evaluation_response.json()
            )

            if evaluation_data.get(
                "interview_completed"
            ):

                return redirect(
                    "report",
                    interview_id=interview_id
                )

        return redirect(
            "interview",
            interview_id=interview_id
        )

    # -----------------------------
    # Get Current Question
    # -----------------------------

    response = requests.get(
        f"http://127.0.0.1:8001/interviews/"
        f"{interview_id}"
    )

    if response.status_code != 200:

        return render(
            request,
            "interview.html",
            {
                "interview": interview,
                "fastapi_interview": {},
                "question_time_limit":
                    interview.question_time_limit,
                "question_count":
                    interview.question_count,
            }
        )

    fastapi_interview = response.json()

    # If interview is completed
    if fastapi_interview.get("completed"):

        return redirect(
            "report",
            interview_id=interview_id
        )

    return render(
        request,
        "interview.html",
        {
            "interview": interview,
            "fastapi_interview": fastapi_interview,
            "question_time_limit":
                interview.question_time_limit,
            "question_count":
                interview.question_count,
        },
    )


@login_required
def report_view(request, interview_id):

    interview = Interview.objects.get(
        id=interview_id,
        user=request.user
    )

    response = requests.get(
        f"http://127.0.0.1:8001/reports/{interview_id}"
    )

    if response.status_code == 404:
        report = None
    else:
        report = response.json()

    return render(
        request,
        "report.html",
        {
            "interview": interview,
            "report": report,
        },
    )


@login_required
def history_view(request):

    interviews = (
        Interview.objects
        .filter(
            user=request.user,
            status="completed"
        )
        .select_related("report")
        .order_by("interview_number")
    )

    return render(
        request,
        "history.html",
        {
            "interviews": interviews
        }
    )

