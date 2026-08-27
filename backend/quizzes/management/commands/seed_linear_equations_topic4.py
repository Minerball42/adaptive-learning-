from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Seed adaptive questions for Mathematics "
        "Chapter 3 Topic 4 - Elimination Method."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        try:
            topic = Topic.objects.get(
                chapter__subject__name="Mathematics",
                chapter__chapter_number=3,
                name="Elimination Method",
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
            title="Elimination Method Quiz",
            defaults={
                "description": (
                    "Adaptive assessment on solving "
                    "pairs of linear equations using "
                    "the elimination method."
                )
            },
        )

        questions = [
            # =====================================================
            # EASY
            # =====================================================
            {
                "question_text": (
                    "The main purpose of the elimination "
                    "method is to:"
                ),
                "option_a": (
                    "Convert equations into quadratic equations"
                ),
                "option_b": (
                    "Remove one variable from the pair"
                ),
                "option_c": (
                    "Draw both equations on a graph"
                ),
                "option_d": (
                    "Multiply the variables together"
                ),
                "correct_answer": "B",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "If x + y = 7 and x - y = 1 "
                    "are added, the resulting equation is:"
                ),
                "option_a": "2x = 8",
                "option_b": "2y = 8",
                "option_c": "x = 8",
                "option_d": "x + y = 8",
                "correct_answer": "A",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "For 2x + y = 7 and "
                    "2x - y = 1, adding the equations "
                    "gives x equal to:"
                ),
                "option_a": "1",
                "option_b": "2",
                "option_c": "3",
                "option_d": "4",
                "correct_answer": "B",
                "difficulty": 1,
            },

            # =====================================================
            # MEDIUM
            # =====================================================
            {
                "question_text": (
                    "Solve 2x + y = 8 and "
                    "x - y = 1 using elimination. "
                    "What is x?"
                ),
                "option_a": "2",
                "option_b": "3",
                "option_c": "4",
                "option_d": "5",
                "correct_answer": "B",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "Solve 3x + 2y = 16 and "
                    "3x - 2y = 8. What is y?"
                ),
                "option_a": "1",
                "option_b": "2",
                "option_c": "3",
                "option_d": "4",
                "correct_answer": "B",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "For 2x + 3y = 12 and "
                    "2x - y = 4, what is y?"
                ),
                "option_a": "1",
                "option_b": "2",
                "option_c": "3",
                "option_d": "4",
                "correct_answer": "B",
                "difficulty": 2,
            },

            # =====================================================
            # HARD
            # =====================================================
            {
                "question_text": (
                    "Solve 2x + 3y = 12 and "
                    "3x - 2y = 5 using elimination. "
                    "What is the solution?"
                ),
                "option_a": "(2, 3)",
                "option_b": "(3, 2)",
                "option_c": "(4, 1)",
                "option_d": "(1, 4)",
                "correct_answer": "B",
                "difficulty": 3,
            },
            {
                "question_text": (
                    "Solve 4x + 3y = 18 and "
                    "2x - 3y = 0. What is the "
                    "solution?"
                ),
                "option_a": "(2, 3)",
                "option_b": "(3, 2)",
                "option_c": "(4, 1)",
                "option_d": "(1, 4)",
                "correct_answer": "B",
                "difficulty": 3,
            },
            {
                "question_text": (
                    "Solve 3x + 4y = 18 and "
                    "5x + 2y = 16 using elimination. "
                    "What is the solution?"
                ),
                "option_a": "(2, 3)",
                "option_b": "(3, 2)",
                "option_c": "(4, 1)",
                "option_d": "(1, 4)",
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
                "Chapter 3 Topic 4 adaptive "
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