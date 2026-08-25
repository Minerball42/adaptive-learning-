from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Create a balanced adaptive quiz bank for "
        "Relationship Between Zeroes and Coefficients "
        "of a Polynomial."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Building Polynomials Topic 2 quiz bank..."
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
                    "Relationship Between Zeroes and "
                    "Coefficients of a Polynomial"
                ),
            )

        except Topic.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "Polynomials Topic 2 was not found. "
                    "Run seed_polynomials first."
                )
            )
            return

        except Topic.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR(
                    "Multiple matching Polynomials "
                    "Topic 2 records were found."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found topic: {topic.name}"
            )
        )

        # ---------------------------------------------------------
        # CREATE OR UPDATE QUIZ
        # ---------------------------------------------------------

        quiz = (
            Quiz.objects
            .filter(topic=topic)
            .order_by("id")
            .first()
        )

        if quiz:

            quiz.title = (
                "Zeroes and Coefficients Quiz"
            )

            quiz.description = (
                "Adaptive assessment on the relationship "
                "between zeroes and coefficients of "
                "quadratic polynomials."
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
                    "Zeroes and Coefficients Quiz"
                ),
                description=(
                    "Adaptive assessment on the relationship "
                    "between zeroes and coefficients of "
                    "quadratic polynomials."
                ),
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created quiz: {quiz.title}"
                )
            )

        # =========================================================
        # EASY QUESTIONS
        # =========================================================

        easy_questions = [
            {
                "question_text": (
                    "For the quadratic polynomial "
                    "x^2 - 5x + 6, what is the sum "
                    "of its zeroes?"
                ),
                "option_a": "-5",
                "option_b": "5",
                "option_c": "6",
                "option_d": "-6",
                "correct_answer": "B",
            },

            {
                "question_text": (
                    "For the quadratic polynomial "
                    "x^2 - 5x + 6, what is the product "
                    "of its zeroes?"
                ),
                "option_a": "5",
                "option_b": "-5",
                "option_c": "6",
                "option_d": "-6",
                "correct_answer": "C",
            },

            {
                "question_text": (
                    "For ax^2 + bx + c, the sum of "
                    "the zeroes is:"
                ),
                "option_a": "b/a",
                "option_b": "-b/a",
                "option_c": "c/a",
                "option_d": "-c/a",
                "correct_answer": "B",
            },
        ]

        # =========================================================
        # MEDIUM QUESTIONS
        # =========================================================

        medium_questions = [
            {
                "question_text": (
                    "For 2x^2 + 7x + 3, what is the "
                    "sum of the zeroes?"
                ),
                "option_a": "7/2",
                "option_b": "-7/2",
                "option_c": "3/2",
                "option_d": "-3/2",
                "correct_answer": "B",
            },

            {
                "question_text": (
                    "For 3x^2 - x - 2, what is the "
                    "product of the zeroes?"
                ),
                "option_a": "2/3",
                "option_b": "-2/3",
                "option_c": "-1/3",
                "option_d": "3/2",
                "correct_answer": "B",
            },

            {
                "question_text": (
                    "A monic quadratic polynomial has "
                    "sum of zeroes 6 and product of "
                    "zeroes 8. Which polynomial is it?"
                ),
                "option_a": "x^2 + 6x + 8",
                "option_b": "x^2 - 6x + 8",
                "option_c": "x^2 + 8x - 6",
                "option_d": "x^2 - 8x + 6",
                "correct_answer": "B",
            },
        ]

        # =========================================================
        # HARD QUESTIONS
        # =========================================================

        hard_questions = [
            {
                "question_text": (
                    "If the sum of two zeroes is -4 "
                    "and their product is -5, which "
                    "monic quadratic polynomial has "
                    "these zeroes?"
                ),
                "option_a": "x^2 - 4x - 5",
                "option_b": "x^2 + 4x - 5",
                "option_c": "x^2 - 4x + 5",
                "option_d": "x^2 + 4x + 5",
                "correct_answer": "B",
            },

            {
                "question_text": (
                    "One zero of 2x^2 - 5x - 3 "
                    "is 3. What is the other zero?"
                ),
                "option_a": "1/2",
                "option_b": "-1/2",
                "option_c": "3/2",
                "option_d": "-3/2",
                "correct_answer": "B",
            },

            {
                "question_text": (
                    "The zeroes of x^2 + kx + 12 "
                    "are 3 and 4. What is the value "
                    "of k?"
                ),
                "option_a": "7",
                "option_b": "-7",
                "option_c": "12",
                "option_d": "-12",
                "correct_answer": "B",
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
        # COUNTS
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

        # ---------------------------------------------------------
        # SUMMARY
        # ---------------------------------------------------------

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Polynomials Topic 2 quiz bank ready."
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
                    question_text=data[
                        "question_text"
                    ],
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
                            data[
                                "correct_answer"
                            ]
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