from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Create a balanced adaptive quiz bank for "
        "Division Algorithm for Polynomials."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Building Polynomials Topic 3 quiz bank..."
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
                name="Division Algorithm for Polynomials",
            )

        except Topic.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "Polynomials Topic 3 was not found. "
                    "Run seed_polynomials first."
                )
            )
            return

        except Topic.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR(
                    "Multiple matching Polynomials "
                    "Topic 3 records were found."
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
                "Division Algorithm for Polynomials Quiz"
            )

            quiz.description = (
                "Adaptive assessment on polynomial "
                "division, quotient and remainder."
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
                    "Division Algorithm for Polynomials Quiz"
                ),
                description=(
                    "Adaptive assessment on polynomial "
                    "division, quotient and remainder."
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
                    "When x^2 + 3x + 2 is divided "
                    "by x + 1, what is the quotient?"
                ),
                "option_a": "x + 1",
                "option_b": "x + 2",
                "option_c": "x - 2",
                "option_d": "x + 3",
                "correct_answer": "B",
            },

            {
                "question_text": (
                    "In the polynomial division formula "
                    "p(x) = g(x)q(x) + r(x), "
                    "what does r(x) represent?"
                ),
                "option_a": "Dividend",
                "option_b": "Divisor",
                "option_c": "Quotient",
                "option_d": "Remainder",
                "correct_answer": "D",
            },

            {
                "question_text": (
                    "When x^2 - 1 is divided by "
                    "x - 1, what is the quotient?"
                ),
                "option_a": "x - 1",
                "option_b": "x + 1",
                "option_c": "x",
                "option_d": "x + 2",
                "correct_answer": "B",
            },
        ]

        # =========================================================
        # MEDIUM QUESTIONS
        # =========================================================

        medium_questions = [
            {
                "question_text": (
                    "When 2x^2 + 5x + 2 is divided "
                    "by x + 2, what is the quotient?"
                ),
                "option_a": "2x + 1",
                "option_b": "2x - 1",
                "option_c": "x + 2",
                "option_d": "2x + 2",
                "correct_answer": "A",
            },

            {
                "question_text": (
                    "When x^3 - 1 is divided by "
                    "x - 1, what is the quotient?"
                ),
                "option_a": "x^2 - x + 1",
                "option_b": "x^2 + x - 1",
                "option_c": "x^2 + x + 1",
                "option_d": "x^2 - 1",
                "correct_answer": "C",
            },

            {
                "question_text": (
                    "When x^3 + 2x^2 + x + 5 is "
                    "divided by x^2 + x + 1, "
                    "what is the remainder?"
                ),
                "option_a": "x + 4",
                "option_b": "-x + 4",
                "option_c": "x - 4",
                "option_d": "-x - 4",
                "correct_answer": "B",
            },
        ]

        # =========================================================
        # HARD QUESTIONS
        # =========================================================

        hard_questions = [
            {
                "question_text": (
                    "When 2x^3 + 3x^2 - 11x - 6 "
                    "is divided by x - 2, what is "
                    "the quotient?"
                ),
                "option_a": "2x^2 + 7x + 3",
                "option_b": "2x^2 - 7x + 3",
                "option_c": "2x^2 + 3x + 7",
                "option_d": "2x^2 + 7x - 3",
                "correct_answer": "A",
            },

            {
                "question_text": (
                    "When x^4 - 1 is divided by "
                    "x^2 - 1, what is the quotient?"
                ),
                "option_a": "x^2 - 1",
                "option_b": "x^2 + 1",
                "option_c": "x^2 + x + 1",
                "option_d": "x^3 + 1",
                "correct_answer": "B",
            },

            {
                "question_text": (
                    "When 3x^3 - 5x^2 + 2x + 7 "
                    "is divided by x^2 - 2x + 1, "
                    "what are the quotient and remainder?"
                ),
                "option_a": (
                    "Quotient = 3x + 1, "
                    "Remainder = x + 6"
                ),
                "option_b": (
                    "Quotient = 3x - 1, "
                    "Remainder = x + 6"
                ),
                "option_c": (
                    "Quotient = 3x + 1, "
                    "Remainder = x - 6"
                ),
                "option_d": (
                    "Quotient = 3x + 2, "
                    "Remainder = x + 5"
                ),
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
                "Polynomials Topic 3 quiz bank ready."
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
                    question_text=data["question_text"],
                    defaults={
                        "option_a": data["option_a"],
                        "option_b": data["option_b"],
                        "option_c": data["option_c"],
                        "option_d": data["option_d"],
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