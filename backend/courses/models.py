from django.db import models


class Grade(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="subjects",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=50, default="English")

    def __str__(self):
        if self.grade:
            return f"{self.grade.name} - {self.name}"
        return self.name


class Chapter(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="chapters"
    )
    name = models.CharField(max_length=200)
    chapter_number = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["chapter_number"]

    def __str__(self):
        return f"{self.subject.name} - Chapter {self.chapter_number}: {self.name}"


class Topic(models.Model):
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="topics"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty = models.IntegerField(default=1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

class LearningContent(models.Model):
    topic = models.OneToOneField(
        Topic,
        on_delete=models.CASCADE,
        related_name="learning_content"
    )

    explanation = models.TextField(
        help_text="Simple explanation of the topic."
    )

    key_concepts = models.TextField(
        blank=True,
        help_text="Important ideas the student should remember."
    )

    easy_method = models.TextField(
        blank=True,
        help_text="Simple step-by-step method for solving problems."
    )

    worked_example = models.TextField(
        blank=True,
        help_text="A worked example with the solution."
    )

    common_mistakes = models.TextField(
        blank=True,
        help_text="Common mistakes students should avoid."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Learning Content - {self.topic.name}"

class Note(models.Model):
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to="notes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title