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
        "Create Karnataka SSLC Class 10 "
        "Polynomials topics and learning content."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding Polynomials curriculum..."
            )
        )

        # ---------------------------------------------------------
        # FIND CURRICULUM
        # ---------------------------------------------------------

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

            subject = Subject.objects.get(
                grade=grade,
                name="Mathematics",
            )

            chapter = Chapter.objects.get(
                subject=subject,
                chapter_number=2,
                name="Polynomials",
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
                    "curriculum data was not found. "
                    "Run seed_kseab first."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found chapter: "
                f"{chapter.chapter_number}. "
                f"{chapter.name}"
            )
        )

        # ---------------------------------------------------------
        # TOPIC 1
        # ---------------------------------------------------------

        topic1, created = Topic.objects.update_or_create(
            chapter=chapter,
            name=(
                "Geometrical Meaning of Zeroes "
                "of a Polynomial"
            ),
            defaults={
                "description": (
                    "Understanding zeroes of a polynomial "
                    "through its graph."
                ),
                "difficulty": 1,
            },
        )

        self.print_status(
            created,
            topic1,
        )

        LearningContent.objects.update_or_create(
            topic=topic1,
            defaults={
                "explanation": (
                    "A zero of a polynomial is a value of x "
                    "for which the value of the polynomial "
                    "becomes zero. On a graph, the zeroes "
                    "are the x-coordinates of the points "
                    "where the graph intersects or touches "
                    "the x-axis."
                ),

                "key_concepts": (
                    "1. p(x) = 0 gives the zeroes of p(x).\n"
                    "2. Zeroes can be identified from a graph.\n"
                    "3. An x-axis intersection corresponds "
                    "to a zero of the polynomial.\n"
                    "4. A linear polynomial can have at most "
                    "one zero.\n"
                    "5. A quadratic polynomial can have at "
                    "most two zeroes."
                ),

                "easy_method": (
                    "Step 1: Look at the polynomial graph.\n"
                    "Step 2: Find where it meets the x-axis.\n"
                    "Step 3: Read the x-coordinate of each "
                    "intersection.\n"
                    "Step 4: Those x-values are the zeroes."
                ),

                "worked_example": (
                    "For p(x) = x - 3:\n"
                    "Set p(x) = 0.\n"
                    "x - 3 = 0\n"
                    "x = 3\n"
                    "Therefore, 3 is the zero of p(x)."
                ),

                "common_mistakes": (
                    "Do not confuse the y-coordinate with "
                    "the zero. The zero is the x-coordinate "
                    "where the graph meets the x-axis."
                ),
            },
        )

        # ---------------------------------------------------------
        # TOPIC 2
        # ---------------------------------------------------------

        topic2, created = Topic.objects.update_or_create(
            chapter=chapter,
            name=(
                "Relationship Between Zeroes and "
                "Coefficients of a Polynomial"
            ),
            defaults={
                "description": (
                    "Studying the relationship between "
                    "the zeroes and coefficients of "
                    "quadratic polynomials."
                ),
                "difficulty": 2,
            },
        )

        self.print_status(
            created,
            topic2,
        )

        LearningContent.objects.update_or_create(
            topic=topic2,
            defaults={
                "explanation": (
                    "For a quadratic polynomial "
                    "ax² + bx + c, if α and β are its "
                    "zeroes, then their sum and product "
                    "are directly related to the "
                    "coefficients."
                ),

                "key_concepts": (
                    "For ax² + bx + c:\n"
                    "Sum of zeroes = α + β = -b/a\n"
                    "Product of zeroes = αβ = c/a"
                ),

                "easy_method": (
                    "Step 1: Identify a, b and c.\n"
                    "Step 2: Use -b/a for the sum.\n"
                    "Step 3: Use c/a for the product.\n"
                    "Step 4: Simplify the values."
                ),

                "worked_example": (
                    "For x² - 5x + 6:\n"
                    "a = 1, b = -5, c = 6\n"
                    "Sum of zeroes = -(-5)/1 = 5\n"
                    "Product of zeroes = 6/1 = 6\n"
                    "The zeroes are 2 and 3, and indeed "
                    "2 + 3 = 5 and 2 × 3 = 6."
                ),

                "common_mistakes": (
                    "Remember the negative sign in -b/a. "
                    "For example, if b = -5, then "
                    "-b = 5."
                ),
            },
        )

        # ---------------------------------------------------------
        # TOPIC 3
        # ---------------------------------------------------------

        topic3, created = Topic.objects.update_or_create(
            chapter=chapter,
            name=(
                "Division Algorithm for Polynomials"
            ),
            defaults={
                "description": (
                    "Dividing one polynomial by another "
                    "using the polynomial division algorithm."
                ),
                "difficulty": 3,
            },
        )

        self.print_status(
            created,
            topic3,
        )

        LearningContent.objects.update_or_create(
            topic=topic3,
            defaults={
                "explanation": (
                    "The division algorithm states that "
                    "for polynomials p(x) and g(x), where "
                    "g(x) is not zero, we can write "
                    "p(x) = g(x)q(x) + r(x), where the "
                    "degree of r(x) is less than the "
                    "degree of g(x)."
                ),

                "key_concepts": (
                    "Dividend = Divisor × Quotient "
                    "+ Remainder.\n"
                    "For polynomials:\n"
                    "p(x) = g(x)q(x) + r(x).\n"
                    "The remainder must have a smaller "
                    "degree than the divisor."
                ),

                "easy_method": (
                    "Step 1: Arrange both polynomials in "
                    "descending powers.\n"
                    "Step 2: Divide the leading term of "
                    "the dividend by the leading term "
                    "of the divisor.\n"
                    "Step 3: Multiply.\n"
                    "Step 4: Subtract.\n"
                    "Step 5: Repeat until the remainder "
                    "has lower degree than the divisor."
                ),

                "worked_example": (
                    "Divide x² + 3x + 2 by x + 1.\n"
                    "x² ÷ x = x.\n"
                    "Multiply: x(x + 1) = x² + x.\n"
                    "Subtract: 2x + 2.\n"
                    "2x ÷ x = 2.\n"
                    "Multiply: 2(x + 1) = 2x + 2.\n"
                    "Remainder = 0.\n"
                    "Therefore quotient = x + 2."
                ),

                "common_mistakes": (
                    "Always arrange terms by descending "
                    "powers and include missing powers "
                    "with coefficient zero when needed."
                ),
            },
        )

        # ---------------------------------------------------------
        # SUMMARY
        # ---------------------------------------------------------

        topics = Topic.objects.filter(
            chapter=chapter
        ).order_by("id")

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Polynomials curriculum ready."
            )
        )

        self.stdout.write(
            f"Chapter ID: {chapter.id}"
        )

        self.stdout.write(
            f"Topics: {topics.count()}"
        )

        for topic in topics:
            self.stdout.write(
                f"Topic ID {topic.id}: "
                f"{topic.name}"
            )

    def print_status(
        self,
        created,
        topic,
    ):
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
            f"{topic.name}"
        )