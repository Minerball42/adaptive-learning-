from django.db import models
from users.models import Student
from quizzes.models import Quiz


class QuizAttempt(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    score = models.FloatField()
    total_questions = models.IntegerField()

    attempted_at = models.DateTimeField(auto_now_add=True)

    synced = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.quiz} - {self.score}"

class Answer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        "quizzes.Question",
        on_delete=models.CASCADE,
        related_name="student_answers"
    )

    selected_answer = models.CharField(max_length=1)

    is_correct = models.BooleanField()

    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.attempt.student} - "
            f"Question {self.question.id}"
        )