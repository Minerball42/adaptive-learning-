from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Ensure a balanced Easy, Medium and Hard "
        "question bank for Fundamental Theorem "
        "of Arithmetic."
    )

    MINIMUM_PER_DIFFICULTY = 3

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Building Topic 2 adaptive question bank..."
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
                chapter__chapter_number=1,
                name="Fundamental Theorem of Arithmetic",
            )

        except Topic.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "Fundamental Theorem of Arithmetic "
                    "topic was not found."
                )
            )
            return

        except Topic.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR(
                    "Multiple matching Topic 2 records "
                    "were found."
                )
            )
            return

        # ---------------------------------------------------------
        # FIND QUIZ
        # ---------------------------------------------------------

        quiz = (
            Quiz.objects
            .filter(topic=topic)
            .order_by("id")
            .first()
        )

        if not quiz:
            self.stdout.write(
                self.style.ERROR(
                    "No quiz exists for this topic. "
                    "Run seed_real_numbers first."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found topic: {topic.name}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Found quiz: {quiz.title}"
            )
        )

        # ---------------------------------------------------------
        # ADDITIONAL EASY QUESTIONS
        # ---------------------------------------------------------

        easy_questions = [
            {
                "question_text": (
                    "Which of the following numbers "
                    "is a prime number?"
                ),
                "option_a": "21",
                "option_b": "29",
                "option_c": "39",
                "option_d": "51",
                "correct_answer": "B",
            },
            {
                "question_text": (
                    "What is the prime factorisation "
                    "of 12?"
                ),
                "option_a": "2 × 6",
                "option_b": "3 × 4",
                "option_c": "2² × 3",
                "option_d": "2 × 3²",
                "correct_answer": "C",
            },
            {
                "question_text": (
                    "Which number is composite?"
                ),
                "option_a": "2",
                "option_b": "3",
                "option_c": "5",
                "option_d": "9",
                "correct_answer": "D",
            },
        ]

        # ---------------------------------------------------------
        # ADDITIONAL MEDIUM QUESTIONS
        # ---------------------------------------------------------

        medium_questions = [
            {
                "question_text": (
                    "What is the prime factorisation "
                    "of 72?"
                ),
                "option_a": "2³ × 3²",
                "option_b": "2² × 3³",
                "option_c": "2 × 3⁴",
                "option_d": "2⁴ × 3",
                "correct_answer": "A",
            },
            {
                "question_text": (
                    "Using prime factorisation, "
                    "what is the HCF of 24 and 36?"
                ),
                "option_a": "6",
                "option_b": "12",
                "option_c": "18",
                "option_d": "24",
                "correct_answer": "B",
            },
            {
                "question_text": (
                    "Using prime factorisation, "
                    "what is the LCM of 12 and 18?"
                ),
                "option_a": "24",
                "option_b": "30",
                "option_c": "36",
                "option_d": "54",
                "correct_answer": "C",
            },
        ]

        # ---------------------------------------------------------
        # ADDITIONAL HARD QUESTIONS
        # ---------------------------------------------------------

        hard_questions = [
            {
                "question_text": (
                    "If a = 2³ × 3² × 5 and "
                    "b = 2² × 3⁴, what is HCF(a, b)?"
                ),
                "option_a": "18",
                "option_b": "24",
                "option_c": "36",
                "option_d": "72",
                "correct_answer": "C",
            },
            {
                "question_text": (
                    "If a = 2³ × 3² × 5 and "
                    "b = 2² × 3⁴, what is LCM(a, b)?"
                ),
                "option_a": "1620",
                "option_b": "2160",
                "option_c": "3240",
                "option_d": "6480",
                "correct_answer": "C",
            },
            {
                "question_text": (
                    "Two positive integers have "
                    "HCF 6 and LCM 180. "
                    "If one number is 30, "
                    "what is the other number?"
                ),
                "option_a": "24",
                "option_b": "30",
                "option_c": "36",
                "option_d": "60",
                "correct_answer": "C",
            },
        ]

        # ---------------------------------------------------------
        # ENSURE EACH DIFFICULTY HAS AT LEAST 3
        # ---------------------------------------------------------

        self.ensure_minimum(
            quiz=quiz,
            difficulty=1,
            questions=easy_questions,
            name="Easy",
        )

        self.ensure_minimum(
            quiz=quiz,
            difficulty=2,
            questions=medium_questions,
            name="Medium",
        )

        self.ensure_minimum(
            quiz=quiz,
            difficulty=3,
            questions=hard_questions,
            name="Hard",
        )

        # ---------------------------------------------------------
        # FINAL COUNTS
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
                "Topic 2 adaptive question bank ready."
            )
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

    def ensure_minimum(
        self,
        quiz,
        difficulty,
        questions,
        name,
    ):
        """
        Add questions only until this difficulty
        contains at least MINIMUM_PER_DIFFICULTY.
        """

        current_count = (
            Question.objects.filter(
                quiz=quiz,
                difficulty=difficulty,
            ).count()
        )

        if (
            current_count
            >= self.MINIMUM_PER_DIFFICULTY
        ):
            self.stdout.write(
                f"{name}: already has "
                f"{current_count} questions."
            )
            return

        for data in questions:

            current_count = (
                Question.objects.filter(
                    quiz=quiz,
                    difficulty=difficulty,
                ).count()
            )

            if (
                current_count
                >= self.MINIMUM_PER_DIFFICULTY
            ):
                break

            question, created = (
                Question.objects.update_or_create(
                    quiz=quiz,
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
                        "difficulty": difficulty,
                    },
                )
            )

            if created:
                message = "CREATED"
                styled_message = (
                    self.style.SUCCESS(
                        message
                    )
                )
            else:
                message = "UPDATED"
                styled_message = (
                    self.style.WARNING(
                        message
                    )
                )

            self.stdout.write(
                f"[{styled_message}] "
                f"{question.question_text}"
            )