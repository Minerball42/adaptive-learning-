from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Create a balanced adaptive quiz bank for "
        "Geometrical Meaning of Zeroes of a Polynomial."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Building Polynomials Topic 1 quiz bank..."
            )
        )

        # ---------------------------------------------------------
        # FIND TOPIC
        # ---------------------------------------------------------

        try:
            topic = Topic.objects.get(
                chapter__subject__grade__academic_year__board__code="KSEAB",
                chapter__subject__grade__academic_year__name="2026-27",
                chapter__subject__grade__name="SSLC Class 10",
                chapter__subject__name="Mathematics",
                chapter__chapter_number=2,
                name=(
                    "Geometrical Meaning of Zeroes "
                    "of a Polynomial"
                ),
            )

        except Topic.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "Polynomials Topic 1 was not found. "
                    "Run seed_polynomials first."
                )
            )
            return

        except Topic.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR(
                    "Multiple matching Polynomials "
                    "Topic 1 records were found."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found topic: {topic.name}"
            )
        )

        # ---------------------------------------------------------
        # CREATE / UPDATE QUIZ
        # ---------------------------------------------------------

        quiz = (
            Quiz.objects
            .filter(topic=topic)
            .order_by("id")
            .first()
        )

        if quiz:

            quiz.title = (
                "Geometrical Meaning of Zeroes Quiz"
            )

            quiz.description = (
                "Adaptive assessment on zeroes of "
                "polynomials and their graphical meaning."
            )

            quiz.save(
                update_fields=[
                    "title",
                    "description",
                ]
            )

            self.stdout.write(
                self.style.WARNING(
                    f"Updated quiz: {quiz.title}"
                )
            )

        else:

            quiz = Quiz.objects.create(
                topic=topic,
                title=(
                    "Geometrical Meaning of Zeroes Quiz"
                ),
                description=(
                    "Adaptive assessment on zeroes of "
                    "polynomials and their graphical meaning."
                ),
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created quiz: {quiz.title}"
                )
            )

        # =========================================================
        # EASY
        # =========================================================

        easy_questions = [
            {
                "question_text": (
                    "What is the zero of the polynomial "
                    "p(x) = x - 4?"
                ),
                "option_a": "-4",
                "option_b": "4",
                "option_c": "0",
                "option_d": "1",
                "correct_answer": "B",
            },
            {
                "question_text": (
                    "On the graph of y = p(x), the zeroes "
                    "of p(x) are represented by:"
                ),
                "option_a": (
                    "The y-coordinates where the graph "
                    "meets the y-axis"
                ),
                "option_b": (
                    "The x-coordinates where the graph "
                    "meets or touches the x-axis"
                ),
                "option_c": (
                    "The highest points of the graph"
                ),
                "option_d": (
                    "The lowest points of the graph"
                ),
                "correct_answer": "B",
            },
            {
                "question_text": (
                    "What is the zero of p(x) = 2x + 6?"
                ),
                "option_a": "3",
                "option_b": "-3",
                "option_c": "6",
                "option_d": "-6",
                "correct_answer": "B",
            },
        ]

        # =========================================================
        # MEDIUM
        # =========================================================

        medium_questions = [
            {
                "question_text": (
                    "A graph of a quadratic polynomial "
                    "intersects the x-axis at x = -2 "
                    "and x = 5. What are its zeroes?"
                ),
                "option_a": "-2 and 5",
                "option_b": "2 and -5",
                "option_c": "-2 only",
                "option_d": "5 only",
                "correct_answer": "A",
            },
            {
                "question_text": (
                    "A parabola touches the x-axis only "
                    "at x = 3. How many distinct real "
                    "zeroes does the polynomial have?"
                ),
                "option_a": "0",
                "option_b": "1",
                "option_c": "2",
                "option_d": "3",
                "correct_answer": "B",
            },
            {
                "question_text": (
                    "If the graph of y = p(x) never "
                    "meets or touches the x-axis, how many "
                    "real zeroes does p(x) have?"
                ),
                "option_a": "0",
                "option_b": "1",
                "option_c": "2",
                "option_d": "Cannot be determined",
                "correct_answer": "A",
            },
        ]

        # =========================================================
        # HARD
        # =========================================================

        hard_questions = [
            {
                "question_text": (
                    "What are the zeroes of "
                    "p(x) = x(x - 2)(x + 3)?"
                ),
                "option_a": "0, 2 and -3",
                "option_b": "0, -2 and 3",
                "option_c": "2 and -3 only",
                "option_d": "0 and 3 only",
                "correct_answer": "A",
            },
            {
                "question_text": (
                    "For p(x) = (x - 1)^2(x + 4), "
                    "what are the distinct real zeroes?"
                ),
                "option_a": "1 only",
                "option_b": "-4 only",
                "option_c": "1 and -4",
                "option_d": "-1 and 4",
                "correct_answer": "C",
            },
            {
                "question_text": (
                    "How many real zeroes does "
                    "p(x) = x^2 + 4 have?"
                ),
                "option_a": "0",
                "option_b": "1",
                "option_c": "2",
                "option_d": "4",
                "correct_answer": "A",
            },
        ]

        # ---------------------------------------------------------
        # SAVE QUESTIONS
        # ---------------------------------------------------------

        self.save_questions(
            quiz=quiz,
            difficulty=1,
            questions=easy_questions,
            label="Easy",
        )

        self.save_questions(
            quiz=quiz,
            difficulty=2,
            questions=medium_questions,
            label="Medium",
        )

        self.save_questions(
            quiz=quiz,
            difficulty=3,
            questions=hard_questions,
            label="Hard",
        )

        # ---------------------------------------------------------
        # SUMMARY
        # ---------------------------------------------------------

        easy_count = Question.objects.filter(
            quiz=quiz,
            difficulty=1,
        ).count()

        medium_count = Question.objects.filter(
            quiz=quiz,
            difficulty=2,
        ).count()

        hard_count = Question.objects.filter(
            quiz=quiz,
            difficulty=3,
        ).count()

        total_count = Question.objects.filter(
            quiz=quiz
        ).count()

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Polynomials Topic 1 quiz bank ready."
            )
        )

        self.stdout.write(
            f"Topic ID: {topic.id}"
        )

        self.stdout.write(
            f"Quiz ID: {quiz.id}"
        )

        self.stdout.write(
            f"Easy: {easy_count}"
        )

        self.stdout.write(
            f"Medium: {medium_count}"
        )

        self.stdout.write(
            f"Hard: {hard_count}"
        )

        self.stdout.write(
            f"Total: {total_count}"
        )

    def save_questions(
        self,
        quiz,
        difficulty,
        questions,
        label,
    ):

        self.stdout.write(
            f"\n{label} questions:"
        )

        for data in questions:

            question, created = (
                Question.objects.update_or_create(
                    quiz=quiz,
                    difficulty=difficulty,
                    question_text=(
                        data["question_text"]
                    ),
                    defaults={
                        "option_a": (
                            data["option_a"]
                        ),
                        "option_b": (
                            data["option_b"]
                        ),
                        "option_c": (
                            data["option_c"]
                        ),
                        "option_d": (
                            data["option_d"]
                        ),
                        "correct_answer": (
                            data["correct_answer"]
                        ),
                    },
                )
            )

            if created:
                status_text = (
                    self.style.SUCCESS(
                        "CREATED"
                    )
                )
            else:
                status_text = (
                    self.style.WARNING(
                        "UPDATED"
                    )
                )

            self.stdout.write(
                f"[{status_text}] "
                f"{question.question_text}"
            )