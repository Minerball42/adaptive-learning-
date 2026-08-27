from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import Topic
from quizzes.models import Quiz, Question


class Command(BaseCommand):
    help = (
        "Seed adaptive questions for Mathematics "
        "Chapter 3 Topic 5 - Applications of "
        "Pair of Linear Equations."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        try:
            topic = Topic.objects.get(
                chapter__subject__name="Mathematics",
                chapter__chapter_number=3,
                name=(
                    "Applications of Pair of "
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
                "Applications of Pair of "
                "Linear Equations Quiz"
            ),
            defaults={
                "description": (
                    "Adaptive assessment on forming "
                    "and solving pairs of linear equations "
                    "from real-life situations."
                )
            },
        )

        questions = [
            # =====================================================
            # EASY
            # =====================================================
            {
                "question_text": (
                    "The sum of two numbers is 20. "
                    "If the numbers are x and y, "
                    "which equation represents this?"
                ),
                "option_a": "x - y = 20",
                "option_b": "x + y = 20",
                "option_c": "xy = 20",
                "option_d": "x / y = 20",
                "correct_answer": "B",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "The difference between two numbers "
                    "is 6. If the larger number is x "
                    "and the smaller is y, the equation is:"
                ),
                "option_a": "x + y = 6",
                "option_b": "y - x = 6",
                "option_c": "x - y = 6",
                "option_d": "xy = 6",
                "correct_answer": "C",
                "difficulty": 1,
            },
            {
                "question_text": (
                    "The sum of two numbers is 14 and "
                    "their difference is 2. "
                    "What are the numbers?"
                ),
                "option_a": "6 and 8",
                "option_b": "5 and 9",
                "option_c": "7 and 7",
                "option_d": "4 and 10",
                "correct_answer": "A",
                "difficulty": 1,
            },

            # =====================================================
            # MEDIUM
            # =====================================================
            {
                "question_text": (
                    "The sum of two numbers is 30 and "
                    "their difference is 6. "
                    "What is the larger number?"
                ),
                "option_a": "12",
                "option_b": "15",
                "option_c": "18",
                "option_d": "24",
                "correct_answer": "C",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "Two pens and one notebook cost "
                    "₹50. One pen and one notebook cost "
                    "₹35. What is the cost of one pen?"
                ),
                "option_a": "₹10",
                "option_b": "₹15",
                "option_c": "₹20",
                "option_d": "₹25",
                "correct_answer": "B",
                "difficulty": 2,
            },
            {
                "question_text": (
                    "A father and son's ages add to "
                    "50 years. The father is 30 years "
                    "older than the son. "
                    "How old is the son?"
                ),
                "option_a": "10 years",
                "option_b": "15 years",
                "option_c": "20 years",
                "option_d": "25 years",
                "correct_answer": "A",
                "difficulty": 2,
            },

            # =====================================================
            # HARD
            # =====================================================
            {
                "question_text": (
                    "Five notebooks and three pens cost "
                    "₹190. Three notebooks and two pens "
                    "cost ₹120. What is the cost of "
                    "one notebook?"
                ),
                "option_a": "₹20",
                "option_b": "₹25",
                "option_c": "₹30",
                "option_d": "₹35",
                "correct_answer": "A",
                "difficulty": 3,
            },
            {
                "question_text": (
                    "A two-digit number has digits whose "
                    "sum is 9. The number is 27 greater "
                    "than the number formed by reversing "
                    "its digits. What is the original number?"
                ),
                "option_a": "36",
                "option_b": "54",
                "option_c": "63",
                "option_d": "72",
                "correct_answer": "C",
                "difficulty": 3,
            },
            {
                "question_text": (
                    "The perimeter of a rectangle is "
                    "50 cm. Its length is 5 cm more "
                    "than its breadth. What is its length?"
                ),
                "option_a": "10 cm",
                "option_b": "15 cm",
                "option_c": "20 cm",
                "option_d": "25 cm",
                "correct_answer": "B",
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
                "Chapter 3 Topic 5 adaptive "
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