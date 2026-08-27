from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Seed adaptive questions for Mathematics "
        "Chapter 3 Topic 2 - Graphical Method and "
        "Nature of Solutions."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        try:
            topic = Topic.objects.get(
                chapter__subject__name="Mathematics",
                chapter__chapter_number=3,
                name=(
                    "Graphical Method and "
                    "Nature of Solutions"
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
                "Graphical Method and "
                "Nature of Solutions Quiz"
            ),
            defaults={
                "description": (
                    "Adaptive assessment on graphical "
                    "solutions and the nature of solutions "
                    "of pairs of linear equations."
                )
            },
        )

        questions = [
            # =====================================================
            # EASY
            # =====================================================
            {
                "question_text": (
                    "When two straight lines intersect "
                    "at exactly one point, the pair of "
                    "linear equations has:"
                ),
                "option_a": "No solution",
                "option_b": "One unique solution",
                "option_c": "Two solutions",
                "option_d": "Infinitely many solutions",
                "correct_answer": "B",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "If two lines are parallel, "
                    "the corresponding pair of linear "
                    "equations has:"
                ),
                "option_a": "One solution",
                "option_b": "Two solutions",
                "option_c": "No solution",
                "option_d": "Infinitely many solutions",
                "correct_answer": "C",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "If two lines completely overlap "
                    "each other, they are called:"
                ),
                "option_a": "Parallel lines",
                "option_b": "Perpendicular lines",
                "option_c": "Intersecting lines",
                "option_d": "Coincident lines",
                "correct_answer": "D",
                "difficulty": 1,
            },

            # =====================================================
            # MEDIUM
            # =====================================================
            {
                "question_text": (
                    "The graphs of x + y = 4 and "
                    "x - y = 2 intersect at which point?"
                ),
                "option_a": "(1, 3)",
                "option_b": "(2, 2)",
                "option_c": "(3, 1)",
                "option_d": "(4, 0)",
                "correct_answer": "C",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "The equations x + y = 5 and "
                    "2x + 2y = 10 represent:"
                ),
                "option_a": "Parallel lines",
                "option_b": "Coincident lines",
                "option_c": "Perpendicular lines",
                "option_d": "Intersecting lines",
                "correct_answer": "B",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "The equations x + y = 4 and "
                    "x + y = 7 represent:"
                ),
                "option_a": "Coincident lines",
                "option_b": "Intersecting lines",
                "option_c": "Parallel lines",
                "option_d": "The same equation",
                "correct_answer": "C",
                "difficulty": 2,
            },

            # =====================================================
            # HARD
            # =====================================================
            {
                "question_text": (
                    "For the equations "
                    "a1x + b1y + c1 = 0 and "
                    "a2x + b2y + c2 = 0, if "
                    "a1/a2 is not equal to b1/b2, "
                    "the pair has:"
                ),
                "option_a": "No solution",
                "option_b": "One unique solution",
                "option_c": "Infinitely many solutions",
                "option_d": "No variables",
                "correct_answer": "B",
                "difficulty": 3,
            },
            {
                "question_text": (
                    "If a1/a2 = b1/b2 but "
                    "a1/a2 is not equal to c1/c2, "
                    "the two equations represent:"
                ),
                "option_a": "Intersecting lines",
                "option_b": "Coincident lines",
                "option_c": "Parallel lines",
                "option_d": "Perpendicular lines",
                "correct_answer": "C",
                "difficulty": 3,
            },
            {
                "question_text": (
                    "If a1/a2 = b1/b2 = c1/c2, "
                    "the pair of linear equations has:"
                ),
                "option_a": "Exactly one solution",
                "option_b": "Exactly two solutions",
                "option_c": "No solution",
                "option_d": "Infinitely many solutions",
                "correct_answer": "D",
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
                    "correct_answer": data["correct_answer"],
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
                "Chapter 3 Topic 2 adaptive "
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