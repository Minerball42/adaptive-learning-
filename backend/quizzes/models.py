from django.db import models
from courses.models import Topic


class Quiz(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

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
        related_name="questions"
    )
    question_text = models.TextField()

    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)

    correct_answer = models.CharField(max_length=1)

    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=1
    )

    def __str__(self):
        return self.question_text