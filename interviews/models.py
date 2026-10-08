

from django.db import models
from django.contrib.auth.models import User


class Interview(models.Model):

    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="interviews"
    )

    interview_number = models.PositiveIntegerField()

    interview_type = models.CharField(
        max_length=20,
        choices=[
            ("technical", "Technical"),
            ("non_technical", "Non-Technical"),
            ("behavioral", "Behavioral"),
        ]
    )

    years_of_experience = models.FloatField(default=0)

    difficulty = models.CharField(max_length=20)

    duration_minutes = models.PositiveIntegerField()

    question_time_limit = models.PositiveIntegerField(
        default=120
    )

    focus_area = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    target_role = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="in_progress"
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    ended_at = models.DateTimeField(
        blank=True,
        null=True
    )

    overall_score = models.FloatField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "interview_number"],
                name="unique_interview_number_per_user"
            )
        ]


    def __str__(self):
        return f"{self.user.username} - Interview {self.interview_number}"
class Message(models.Model):

    ROLE_CHOICES = [
        ("interviewer", "Interviewer"),
        ("user", "User"),
    ]

    STATUS_CHOICES = [
        ("asked", "Asked"),
        ("answered", "Answered"),
        ("skipped", "Skipped"),
    ]

    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    content = models.TextField()

    message_number = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="asked"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.interview} - Message {self.message_number}"
class Evaluation(models.Model):

    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name="evaluations"
    )

    answer_message = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        related_name="evaluation"
    )

    technical_score = models.FloatField()
    communication_score = models.FloatField()
    relevance_score = models.FloatField()
    depth_score = models.FloatField()
    overall_score = models.FloatField()

    strengths = models.TextField(
        blank=True,
        null=True
    )

    weaknesses = models.TextField(
        blank=True,
        null=True
    )

    feedback = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Evaluation - {self.answer_message}"
class Report(models.Model):

    interview = models.OneToOneField(
        Interview,
        on_delete=models.CASCADE,
        related_name="report"
    )

    overall_score = models.FloatField()

    strengths = models.TextField(
        blank=True,
        null=True
    )

    weaknesses = models.TextField(
        blank=True,
        null=True
    )

    recommendations = models.TextField(
        blank=True,
        null=True
    )

    final_feedback = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Report - {self.interview}"