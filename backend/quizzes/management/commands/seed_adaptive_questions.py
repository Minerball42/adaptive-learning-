from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Create a balanced Easy, Medium and Hard "
        "question bank for Real Numbers Topic 1"
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Building adaptive question bank..."
            )
        )

        # ---------------------------------------------------------
        # FIND REAL NUMBERS TOPIC 1
        # ---------------------------------------------------------

        try:
            topic = Topic.objects.get(
                chapter__subject__grade__academic_year__board__code="KSEAB",
                chapter__subject__grade__academic_year__name="2026-27",
                chapter__subject__grade__name="SSLC Class 10",
                chapter__subject__name="Mathematics",
                chapter__chapter_number=1,
                name="Introduction to Real Numbers",
            )

        except Topic.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "Introduction to Real Numbers "
                    "topic was not found."
                )
            )
            return

        except Topic.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR(
                    "Multiple matching topics were found. "
                    "Please check the curriculum data."
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
                    "Quiz was not found. Run "
                    "'python manage.py seed_real_numbers' first."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found quiz: {quiz.title}"
            )
        )

        # ---------------------------------------------------------
        # QUESTION BANK
        # ---------------------------------------------------------

        questions = [

            # =====================================================
            # EASY
            # =====================================================

            {
                "question_text": (
                    "Which of the following is a "
                    "rational number?"
                ),
                "option_a": "√2",
                "option_b": "√3",
                "option_c": "3/5",
                "option_d": "π",
                "correct_answer": "C",
                "difficulty": 1,
            },

            {
                "question_text": (
                    "Which number is irrational?"
                ),
                "option_a": "0.5",
                "option_b": "3/4",
                "option_c": "√2",
                "option_d": "7",
                "correct_answer": "C",
                "difficulty": 1,
            },

            {
                "question_text": (
                    "Which statement about rational "
                    "numbers is correct?"
                ),
                "option_a": (
                    "They cannot be written as fractions"
                ),
                "option_b": (
                    "They can be written as p/q "
                    "where q is not zero"
                ),
                "option_c": (
                    "They are always negative"
                ),
                "option_d": (
                    "They never contain decimals"
                ),
                "correct_answer": "B",
                "difficulty": 1,
            },

            # =====================================================
            # MEDIUM
            # =====================================================

            {
                "question_text": (
                    "Which of the following belongs "
                    "to the set of real numbers?"
                ),
                "option_a": "Only integers",
                "option_b": "Only rational numbers",
                "option_c": "Only irrational numbers",
                "option_d": (
                    "Both rational and irrational numbers"
                ),
                "correct_answer": "D",
                "difficulty": 2,
            },

            {
                "question_text": (
                    "Which of the following is rational?"
                ),
                "option_a": "π",
                "option_b": "√5",
                "option_c": "0.25",
                "option_d": "√7",
                "correct_answer": "C",
                "difficulty": 2,
            },

            {
                "question_text": (
                    "Which decimal represents "
                    "a rational number?"
                ),
                "option_a": "0.101001000100001...",
                "option_b": "0.272727...",
                "option_c": "π",
                "option_d": "√2",
                "correct_answer": "B",
                "difficulty": 2,
            },

            # =====================================================
            # HARD
            # =====================================================

            {
                "question_text": (
                    "Simplify √2 + √8 and classify "
                    "the result."
                ),
                "option_a": "2√2, rational",
                "option_b": "3, rational",
                "option_c": "3√2, irrational",
                "option_d": "4√2, irrational",
                "correct_answer": "C",
                "difficulty": 3,
            },

            {
                "question_text": (
                    "Which statement is true?"
                ),
                "option_a": (
                    "The sum of two irrational numbers "
                    "is always irrational"
                ),
                "option_b": (
                    "The product of two irrational numbers "
                    "can be rational"
                ),
                "option_c": (
                    "Every non-terminating decimal "
                    "is irrational"
                ),
                "option_d": (
                    "Every square root is irrational"
                ),
                "correct_answer": "B",
                "difficulty": 3,
            },

            {
                "question_text": (
                    "The number 3√5 is:"
                ),
                "option_a": "An integer",
                "option_b": "A rational number",
                "option_c": "A natural number",
                "option_d": "An irrational number",
                "correct_answer": "D",
                "difficulty": 3,
            },
        ]

        # ---------------------------------------------------------
        # CREATE / UPDATE QUESTIONS
        # ---------------------------------------------------------

        created_count = 0
        updated_count = 0

        for data in questions:

            question, created = (
                Question.objects.update_or_create(
                    quiz=quiz,
                    question_text=data["question_text"],
                    defaults={
                        "option_a": data["option_a"],
                        "option_b": data["option_b"],
                        "option_c": data["option_c"],
                        "option_d": data["option_d"],
                        "correct_answer": (
                            data["correct_answer"]
                        ),
                        "difficulty": data["difficulty"],
                    },
                )
            )

            if created:
                created_count += 1

                status_text = self.style.SUCCESS(
                    "CREATED"
                )

            else:
                updated_count += 1

                status_text = self.style.WARNING(
                    "UPDATED"
                )

            self.stdout.write(
                f"[{status_text}] "
                f"{question.question_text}"
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
                "Adaptive question bank ready."
            )
        )

        self.stdout.write(
            f"Created: {created_count}"
        )

        self.stdout.write(
            f"Updated: {updated_count}"
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