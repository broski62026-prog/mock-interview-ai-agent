from django.urls import path

from .views import (
    interview_setup_view,
    interview_view,
    report_view,
    history_view,
)


urlpatterns = [

    path(
        "interview/setup/",
        interview_setup_view,
        name="interview_setup"
    ),

    path(
        "interview/<int:interview_id>/",
        interview_view,
        name="interview"
    ),

    path(
        "report/<int:interview_id>/",
        report_view,
        name="report"
    ),

    path(
        "history/",
        history_view,
        name="history"
    ),

]