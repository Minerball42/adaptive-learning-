from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import (
    Board,
    AcademicYear,
    Grade,
    Subject,
    Chapter,
    Topic,
    LearningContent,
)


class Command(BaseCommand):
    help = (
        "Seed KSEAB SSLC Class 10 Mathematics "
        "Chapter 3 - Pair of Linear Equations "
        "in Two Variables."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding Pair of Linear Equations "
                "in Two Variables..."
            )
        )

        # =========================================================
        # LOCATE CURRICULUM
        # =========================================================

        try:

            board = Board.objects.get(
                code="KSEAB"
            )

            academic_year = AcademicYear.objects.get(
                board=board,
                name="2026-27",
            )

            grade = Grade.objects.get(
                academic_year=academic_year,
                name="SSLC Class 10",
            )

            mathematics = Subject.objects.get(
                grade=grade,
                name="Mathematics",
                subject_type="core",
            )

            chapter = Chapter.objects.get(
                subject=mathematics,
                chapter_number=3,
            )

        except (
            Board.DoesNotExist,
            AcademicYear.DoesNotExist,
            Grade.DoesNotExist,
            Subject.DoesNotExist,
            Chapter.DoesNotExist,
        ):

            self.stdout.write(
                self.style.ERROR(
                    "Required KSEAB Mathematics "
                    "curriculum was not found. "
                    "Run seed_kseab first."
                )
            )

            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found chapter: {chapter}"
            )
        )

        # =========================================================
        # TOPIC 1
        # INTRODUCTION
        # =========================================================

        topic_1 = self._create_topic(
            chapter=chapter,
            name=(
                "Introduction to Pair of "
                "Linear Equations"
            ),
            description=(
                "Understanding linear equations "
                "in two variables and pairs of "
                "linear equations."
            ),
            difficulty=1,
        )

        LearningContent.objects.update_or_create(
            topic=topic_1,
            defaults={
                "explanation": (
                    "A linear equation in two variables "
                    "can be written in the form "
                    "ax + by + c = 0, where a and b "
                    "are not both zero. A pair of linear "
                    "equations consists of two such "
                    "equations involving the same variables."
                ),

                "key_concepts": (
                    "1. General form: ax + by + c = 0.\n"
                    "2. A solution is an ordered pair (x, y).\n"
                    "3. The solution must satisfy both "
                    "equations simultaneously.\n"
                    "4. Each linear equation represents "
                    "a straight line on a graph."
                ),

                "easy_method": (
                    "Step 1: Identify x and y.\n"
                    "Step 2: Write each equation in standard "
                    "linear form.\n"
                    "Step 3: Check whether a given ordered "
                    "pair satisfies both equations."
                ),

                "worked_example": (
                    "Consider:\n"
                    "x + y = 5\n"
                    "x - y = 1\n\n"
                    "For x = 3 and y = 2:\n"
                    "3 + 2 = 5\n"
                    "3 - 2 = 1\n\n"
                    "Therefore, (3, 2) satisfies both "
                    "equations and is their common solution."
                ),

                "common_mistakes": (
                    "Do not check a solution in only one "
                    "equation. It must satisfy both equations."
                ),
            },
        )

        # =========================================================
        # TOPIC 2
        # GRAPHICAL METHOD
        # =========================================================

        topic_2 = self._create_topic(
            chapter=chapter,
            name=(
                "Graphical Method and "
                "Nature of Solutions"
            ),
            description=(
                "Solving pairs of linear equations "
                "graphically and identifying unique, "
                "no, or infinitely many solutions."
            ),
            difficulty=2,
        )

        LearningContent.objects.update_or_create(
            topic=topic_2,
            defaults={
                "explanation": (
                    "Each linear equation represents a "
                    "straight line. When two equations are "
                    "drawn on the same graph, their relative "
                    "positions determine the number of "
                    "solutions."
                ),

                "key_concepts": (
                    "1. Intersecting lines: one unique "
                    "solution.\n"
                    "2. Parallel lines: no solution.\n"
                    "3. Coincident lines: infinitely many "
                    "solutions.\n"
                    "4. The intersection point gives the "
                    "common solution."
                ),

                "easy_method": (
                    "Step 1: Find at least two points for "
                    "each equation.\n"
                    "Step 2: Plot the points.\n"
                    "Step 3: Draw both straight lines.\n"
                    "Step 4: Observe whether they intersect, "
                    "remain parallel, or coincide."
                ),

                "worked_example": (
                    "For:\n"
                    "x + y = 4\n"
                    "x - y = 2\n\n"
                    "The two lines intersect at (3, 1).\n"
                    "Therefore the pair has one unique "
                    "solution: x = 3, y = 1."
                ),

                "common_mistakes": (
                    "Plot points carefully. A small plotting "
                    "error can give an incorrect intersection "
                    "point."
                ),
            },
        )

        # =========================================================
        # TOPIC 3
        # SUBSTITUTION METHOD
        # =========================================================

        topic_3 = self._create_topic(
            chapter=chapter,
            name="Substitution Method",
            description=(
                "Solving a pair of linear equations "
                "by expressing one variable in terms "
                "of the other."
            ),
            difficulty=2,
        )

        LearningContent.objects.update_or_create(
            topic=topic_3,
            defaults={
                "explanation": (
                    "In the substitution method, one "
                    "equation is rearranged to express one "
                    "variable in terms of the other. This "
                    "expression is substituted into the "
                    "second equation."
                ),

                "key_concepts": (
                    "1. Isolate one variable.\n"
                    "2. Substitute it into the other "
                    "equation.\n"
                    "3. Solve for one variable.\n"
                    "4. Substitute back to find the other."
                ),

                "easy_method": (
                    "Step 1: Choose the easiest equation.\n"
                    "Step 2: Make x or y the subject.\n"
                    "Step 3: Substitute into the second "
                    "equation.\n"
                    "Step 4: Solve.\n"
                    "Step 5: Substitute back."
                ),

                "worked_example": (
                    "x + y = 7\n"
                    "x - y = 1\n\n"
                    "From x + y = 7:\n"
                    "x = 7 - y\n\n"
                    "Substitute into x - y = 1:\n"
                    "7 - y - y = 1\n"
                    "7 - 2y = 1\n"
                    "y = 3\n\n"
                    "Then x = 4.\n"
                    "Solution: (4, 3)."
                ),

                "common_mistakes": (
                    "Use brackets correctly while "
                    "substituting expressions containing "
                    "negative signs."
                ),
            },
        )

        # =========================================================
        # TOPIC 4
        # ELIMINATION METHOD
        # =========================================================

        topic_4 = self._create_topic(
            chapter=chapter,
            name="Elimination Method",
            description=(
                "Solving a pair of linear equations "
                "by eliminating one variable."
            ),
            difficulty=2,
        )

        LearningContent.objects.update_or_create(
            topic=topic_4,
            defaults={
                "explanation": (
                    "In the elimination method, the "
                    "coefficients of one variable are made "
                    "equal or opposite. The equations are "
                    "then added or subtracted to eliminate "
                    "that variable."
                ),

                "key_concepts": (
                    "1. Choose a variable to eliminate.\n"
                    "2. Make its coefficients equal or "
                    "opposite.\n"
                    "3. Add or subtract the equations.\n"
                    "4. Solve the remaining equation.\n"
                    "5. Substitute back."
                ),

                "easy_method": (
                    "Step 1: Compare coefficients.\n"
                    "Step 2: Multiply equations if needed.\n"
                    "Step 3: Add or subtract.\n"
                    "Step 4: Find one variable.\n"
                    "Step 5: Substitute to find the other."
                ),

                "worked_example": (
                    "2x + y = 8\n"
                    "x - y = 1\n\n"
                    "Add the equations:\n"
                    "3x = 9\n"
                    "x = 3\n\n"
                    "Substitute into x - y = 1:\n"
                    "3 - y = 1\n"
                    "y = 2\n\n"
                    "Solution: (3, 2)."
                ),

                "common_mistakes": (
                    "When multiplying an equation, multiply "
                    "every term, not only the variable term."
                ),
            },
        )

        # =========================================================
        # TOPIC 5
        # APPLICATION PROBLEMS
        # =========================================================

        topic_5 = self._create_topic(
            chapter=chapter,
            name=(
                "Applications of Pair of "
                "Linear Equations"
            ),
            description=(
                "Forming and solving pairs of equations "
                "from real-life situations."
            ),
            difficulty=3,
        )

        LearningContent.objects.update_or_create(
            topic=topic_5,
            defaults={
                "explanation": (
                    "Many real-life situations involving "
                    "two unknown quantities can be modeled "
                    "using a pair of linear equations."
                ),

                "key_concepts": (
                    "1. Identify the two unknown quantities.\n"
                    "2. Assign variables.\n"
                    "3. Translate each condition into an "
                    "equation.\n"
                    "4. Solve the pair using substitution "
                    "or elimination.\n"
                    "5. Interpret the answer in context."
                ),

                "easy_method": (
                    "Step 1: Read the problem carefully.\n"
                    "Step 2: Let the unknowns be x and y.\n"
                    "Step 3: Create two equations.\n"
                    "Step 4: Solve them.\n"
                    "Step 5: Check whether the answer makes "
                    "sense in the original problem."
                ),

                "worked_example": (
                    "The sum of two numbers is 30 and their "
                    "difference is 6.\n\n"
                    "Let the numbers be x and y.\n"
                    "x + y = 30\n"
                    "x - y = 6\n\n"
                    "Adding:\n"
                    "2x = 36\n"
                    "x = 18\n\n"
                    "Then y = 12.\n"
                    "The numbers are 18 and 12."
                ),

                "common_mistakes": (
                    "Do not start solving before converting "
                    "all conditions into correct equations."
                ),
            },
        )

        # =========================================================
        # SUMMARY
        # =========================================================

        topics = Topic.objects.filter(
            chapter=chapter
        ).order_by("id")

        lessons = LearningContent.objects.filter(
            topic__chapter=chapter
        )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Chapter 3 curriculum seeded successfully."
            )
        )

        self.stdout.write(
            f"Chapter: {chapter.name}"
        )

        self.stdout.write(
            f"Topics: {topics.count()}"
        )

        self.stdout.write(
            f"Learning contents: {lessons.count()}"
        )

        for topic in topics:

            self.stdout.write(
                f"Topic ID {topic.id}: "
                f"{topic.name}"
            )

    # =============================================================
    # HELPERS
    # =============================================================

    def _create_topic(
        self,
        chapter,
        name,
        description,
        difficulty,
    ):

        topic, created = (
            Topic.objects.update_or_create(
                chapter=chapter,
                name=name,
                defaults={
                    "description": description,
                    "difficulty": difficulty,
                },
            )
        )

        if created:

            state = self.style.SUCCESS(
                "CREATED"
            )

        else:

            state = self.style.WARNING(
                "UPDATED"
            )

        self.stdout.write(
            f"[{state}] Topic: {topic.name}"
        )

        return topic