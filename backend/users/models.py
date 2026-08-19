from django.db import models
from django.contrib.auth.models import User
from courses.models import Grade


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    grade = models.ForeignKey(
        Grade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students"
    )

    school = models.CharField(max_length=200)

    preferred_language = models.CharField(
        max_length=50,
        default="English"
    )

    def __str__(self):
        return self.user.username


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username