from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Seed adaptive questions for "
        "Mathematics Chapter 3 Topic 1 - "
        "Introduction to Pair of Linear Equations."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        try:
            topic = Topic.objects.get(
                chapter__subject__name="Mathematics",
                chapter__chapter_number=3,
                name=(
                    "Introduction to Pair of "
                    "Linear Equations"
                ),
            )

        except Topic.DoesNotExist:

            self.stdout.write(
                self.style.ERROR(
                    "Topic not found. Run "
                    "seed_linear_equations first."
                )
            )

            return

        quiz, _ = Quiz.objects.update_or_create(
            topic=topic,
            title=(
                "Introduction to Pair of "
                "Linear Equations Quiz"
            ),
            defaults={
                "description": (
                    "Adaptive assessment on basic "
                    "concepts of pairs of linear "
                    "equations in two variables."
                )
            },
        )

        questions = [
            # =====================================================
            # EASY
            # =====================================================
            {
                "question_text": (
                    "Which of the following is a "
                    "linear equation in two variables?"
                ),
                "option_a": "x² + y = 5",
                "option_b": "2x + 3y = 7",
                "option_c": "xy = 6",
                "option_d": "1/x + y = 4",
                "correct_answer": "B",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "The general form of a linear "
                    "equation in two variables is:"
                ),
                "option_a": "ax² + by = 0",
                "option_b": "ax + by + c = 0",
                "option_c": "ax + by² = 0",
                "option_d": "axy + c = 0",
                "correct_answer": "B",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "Which ordered pair satisfies "
                    "x + y = 5?"
                ),
                "option_a": "(1, 1)",
                "option_b": "(2, 2)",
                "option_c": "(2, 3)",
                "option_d": "(5, 5)",
                "correct_answer": "C",
                "difficulty": 1,
            },

            # =====================================================
            # MEDIUM
            # =====================================================
            {
                "question_text": (
                    "Which ordered pair satisfies both "
                    "x + y = 7 and x - y = 1?"
                ),
                "option_a": "(4, 3)",
                "option_b": "(3, 4)",
                "option_c": "(5, 2)",
                "option_d": "(6, 1)",
                "correct_answer": "A",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "If (2, 3) is substituted into "
                    "2x + y = 7, what happens?"
                ),
                "option_a": "The equation is satisfied",
                "option_b": "The left side becomes 5",
                "option_c": "The left side becomes 6",
                "option_d": "The equation has no variables",
                "correct_answer": "A",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "A common solution of two linear "
                    "equations must:"
                ),
                "option_a": (
                    "Satisfy only the first equation"
                ),
                "option_b": (
                    "Satisfy only the second equation"
                ),
                "option_c": (
                    "Satisfy both equations"
                ),
                "option_d": (
                    "Make both equations quadratic"
                ),
                "correct_answer": "C",
                "difficulty": 2,
            },

            # =====================================================
            # HARD
            # =====================================================
            {
                "question_text": (
                    "For which value of y does "
                    "(3, y) satisfy 2x + y = 10?"
                ),
                "option_a": "2",
                "option_b": "3",
                "option_c": "4",
                "option_d": "5",
                "correct_answer": "C",
                "difficulty": 3,
            },
            {
                "question_text": (
                    "If (k, 2) satisfies "
                    "3x + 2y = 13, then k is:"
                ),
                "option_a": "2",
                "option_b": "3",
                "option_c": "4",
                "option_d": "5",
                "correct_answer": "B",
                "difficulty": 3,
            },
            {
                "question_text": (
                    "Which pair of equations has "
                    "(2, 1) as a common solution?"
                ),
                "option_a": (
                    "x + y = 3 and x - y = 1"
                ),
                "option_b": (
                    "x + y = 4 and x - y = 1"
                ),
                "option_c": (
                    "2x + y = 6 and x + y = 3"
                ),
                "option_d": (
                    "x + 2y = 5 and x - y = 0"
                ),
                "correct_answer": "A",
                "difficulty": 3,
            },
        ]

        created_count = 0
        updated_count = 0

        for data in questions:

            _, created = Question.objects.update_or_create(
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

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Chapter 3 Topic 1 adaptive "
                "question bank ready."
            )
        )

        self.stdout.write(
            f"Topic ID: {topic.id}"
        )

        self.stdout.write(
            f"Quiz ID: {quiz.id}"
        )

        self.stdout.write(
            f"Created: {created_count}"
        )

        self.stdout.write(
            f"Updated: {updated_count}"
        )

        self.stdout.write(
            f"Total Questions: "
            f"{quiz.questions.count()}"
        )

        for difficulty, name in [
            (1, "Easy"),
            (2, "Medium"),
            (3, "Hard"),
        ]:

            self.stdout.write(
                f"{name}: "
                f"{quiz.questions.filter(
                    difficulty=difficulty
                ).count()}"
            )