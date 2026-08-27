from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Seed adaptive questions for Mathematics "
        "Chapter 3 Topic 3 - Substitution Method."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        try:
            topic = Topic.objects.get(
                chapter__subject__name="Mathematics",
                chapter__chapter_number=3,
                name="Substitution Method",
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
            title="Substitution Method Quiz",
            defaults={
                "description": (
                    "Adaptive assessment on solving "
                    "pairs of linear equations using "
                    "the substitution method."
                )
            },
        )

        questions = [
            # =====================================================
            # EASY
            # =====================================================
            {
                "question_text": (
                    "In the substitution method, "
                    "the first step is usually to:"
                ),
                "option_a": (
                    "Multiply both equations together"
                ),
                "option_b": (
                    "Express one variable in terms "
                    "of the other"
                ),
                "option_c": (
                    "Draw a graph immediately"
                ),
                "option_d": (
                    "Remove both variables"
                ),
                "correct_answer": "B",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "From x + y = 7, expressing x "
                    "in terms of y gives:"
                ),
                "option_a": "x = y - 7",
                "option_b": "x = 7 + y",
                "option_c": "x = 7 - y",
                "option_d": "x = y / 7",
                "correct_answer": "C",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "From y = x + 2, if x = 3, "
                    "what is y?"
                ),
                "option_a": "1",
                "option_b": "5",
                "option_c": "6",
                "option_d": "9",
                "correct_answer": "B",
                "difficulty": 1,
            },

            # =====================================================
            # MEDIUM
            # =====================================================
            {
                "question_text": (
                    "Solve using substitution: "
                    "x + y = 7 and x - y = 1. "
                    "What is x?"
                ),
                "option_a": "2",
                "option_b": "3",
                "option_c": "4",
                "option_d": "5",
                "correct_answer": "C",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "For x + y = 9 and x = y + 3, "
                    "what is y?"
                ),
                "option_a": "2",
                "option_b": "3",
                "option_c": "4",
                "option_d": "6",
                "correct_answer": "B",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "Given y = 2x and x + y = 9, "
                    "what is x?"
                ),
                "option_a": "2",
                "option_b": "3",
                "option_c": "4",
                "option_d": "6",
                "correct_answer": "B",
                "difficulty": 2,
            },

            # =====================================================
            # HARD
            # =====================================================
            {
                "question_text": (
                    "Solve using substitution: "
                    "2x + y = 11 and y = x + 2. "
                    "What is x?"
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
                    "If x = 2y - 1 and "
                    "3x + y = 18, what is y?"
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
                    "Solve the pair "
                    "2x + 3y = 12 and x = 3 - y. "
                    "What is the solution?"
                ),
                "option_a": "(3, 1)",
                "option_b": "(2, 2)",
                "option_c": "(1, 3)",
                "option_d": "(0, 4)",
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
                "Chapter 3 Topic 3 adaptive "
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

            count = quiz.questions.filter(
                difficulty=difficulty
            ).count()

            self.stdout.write(
                f"{name}: {count}"
            )