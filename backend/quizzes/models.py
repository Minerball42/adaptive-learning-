import uuid

from django.db import models

from courses.models import Topic
from users.models import Student


class Quiz(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="quizzes",
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.title


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        (1, "Easy"),
        (2, "Medium"),
        (3, "Hard"),
    ]

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_text = models.TextField()

    option_a = models.CharField(
        max_length=300
    )

    option_b = models.CharField(
        max_length=300
    )

    option_c = models.CharField(
        max_length=300
    )

    option_d = models.CharField(
        max_length=300
    )

    correct_answer = models.CharField(
        max_length=1
    )

    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=1,
    )

    def __str__(self):
        return self.question_text


class AdaptiveQuizSession(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="adaptive_quiz_sessions",
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="adaptive_sessions",
    )

    questions = models.ManyToManyField(
        Question,
        related_name="adaptive_sessions",
    )

    target_difficulty = models.IntegerField(
        choices=Question.DIFFICULTY_CHOICES
    )

    mastery_score_before = models.FloatField(
        default=0
    )

    mastery_level_before = models.CharField(
        max_length=20,
        default="not_started",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.quiz} - "
            f"{self.status}"
        )