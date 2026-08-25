from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Ensure a balanced Easy, Medium and Hard "
        "question bank for Revisiting Irrational Numbers."
    )

    MINIMUM_PER_DIFFICULTY = 3

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Building Topic 3 adaptive question bank..."
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
                name="Revisiting Irrational Numbers",
            )

        except Topic.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "Revisiting Irrational Numbers topic "
                    "was not found."
                )
            )
            return

        except Topic.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR(
                    "Multiple matching Topic 3 records "
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
                    "No quiz exists for Topic 3. "
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

        # =========================================================
        # EASY
        # =========================================================

        easy_questions = [
            {
                "question_text": (
                    "Which of the following numbers "
                    "is irrational?"
                ),
                "option_a": "1/2",
                "option_b": "0.75",
                "option_c": "√2",
                "option_d": "5",
                "correct_answer": "C",
            },
            {
                "question_text": (
                    "Which decimal expansion represents "
                    "an irrational number?"
                ),
                "option_a": "0.625",
                "option_b": "0.272727...",
                "option_c": "0.101001000100001...",
                "option_d": "2.5",
                "correct_answer": "C",
            },
            {
                "question_text": (
                    "Which square root is an "
                    "irrational number?"
                ),
                "option_a": "√4",
                "option_b": "√9",
                "option_c": "√16",
                "option_d": "√7",
                "correct_answer": "D",
            },
        ]

        # =========================================================
        # MEDIUM
        # =========================================================

        medium_questions = [
            {
                "question_text": (
                    "Which of the following square-root "
                    "values is irrational?"
                ),
                "option_a": "√49",
                "option_b": "√7",
                "option_c": "√81",
                "option_d": "√100",
                "correct_answer": "B",
            },
            {
                "question_text": (
                    "If x is irrational, which expression "
                    "must remain irrational?"
                ),
                "option_a": "x + 0",
                "option_b": "x - x",
                "option_c": "x / x",
                "option_d": "0 × x",
                "correct_answer": "A",
            },
            {
                "question_text": (
                    "Which number has a non-terminating "
                    "and non-repeating decimal expansion?"
                ),
                "option_a": "3/8",
                "option_b": "7/11",
                "option_c": "√3",
                "option_d": "5/2",
                "correct_answer": "C",
            },
        ]

        # =========================================================
        # HARD
        # =========================================================

        hard_questions = [
            {
                "question_text": (
                    "Which of the following expressions "
                    "is irrational?"
                ),
                "option_a": "√2 × √8",
                "option_b": "√3 × √3",
                "option_c": "√2 + √3",
                "option_d": "√25",
                "correct_answer": "C",
            },
            {
                "question_text": (
                    "Suppose 3 + 2√5 were rational. "
                    "Which conclusion would contradict "
                    "the fact that √5 is irrational?"
                ),
                "option_a": (
                    "√5 would have to be rational"
                ),
                "option_b": (
                    "3 would have to be irrational"
                ),
                "option_c": (
                    "2 would have to be irrational"
                ),
                "option_d": (
                    "5 would have to be negative"
                ),
                "correct_answer": "A",
            },
            {
                "question_text": (
                    "Which statement about rational and "
                    "irrational numbers is always true?"
                ),
                "option_a": (
                    "The sum of two irrational numbers "
                    "is always irrational"
                ),
                "option_b": (
                    "The product of two irrational numbers "
                    "is always irrational"
                ),
                "option_c": (
                    "A rational number plus a non-zero "
                    "irrational number is irrational"
                ),
                "option_d": (
                    "Every square root is irrational"
                ),
                "correct_answer": "C",
            },
        ]

        # ---------------------------------------------------------
        # ENSURE MINIMUM
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
                "Topic 3 adaptive question bank ready."
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
        Add questions until this difficulty has
        at least MINIMUM_PER_DIFFICULTY questions.

        Important:
        Difficulty is part of the lookup so an
        existing question cannot be moved from
        Easy to Medium or Hard.
        """

        current_count = (
            Question.objects.filter(
                quiz=quiz,
                difficulty=difficulty,
            ).count()
        )

        if current_count >= self.MINIMUM_PER_DIFFICULTY:
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

            if current_count >= self.MINIMUM_PER_DIFFICULTY:
                break

            question, created = (
                Question.objects.update_or_create(
                    quiz=quiz,

                    # IMPORTANT FIX
                    difficulty=difficulty,

                    question_text=(
                        data["question_text"]
                    ),

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