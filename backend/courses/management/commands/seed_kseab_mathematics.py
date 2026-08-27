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


# ================================================================
# KSEAB SSLC MATHEMATICS
# CHAPTERS 4-14
#
# Chapters 1-3 are intentionally NOT modified here because
# they already contain quizzes, attempts and student progress.
# ================================================================


MATHEMATICS_DATA = {
    4: {
        "chapter": "Quadratic Equations",
        "topics": [
            {
                "name": "Introduction to Quadratic Equations",
                "difficulty": 1,
                "explanation": (
                    "A quadratic equation is an equation of "
                    "degree two. Its standard form is "
                    "ax² + bx + c = 0, where a is not zero."
                ),
                "key_concepts": (
                    "Standard form: ax² + bx + c = 0.\n"
                    "The highest power of x is 2.\n"
                    "The coefficient a cannot be zero."
                ),
                "worked_example": (
                    "x² + 5x + 6 = 0 is quadratic because "
                    "the highest power of x is 2."
                ),
            },
            {
                "name": "Solution by Factorisation",
                "difficulty": 2,
                "explanation": (
                    "A quadratic equation can sometimes be "
                    "solved by expressing it as a product "
                    "of two linear factors."
                ),
                "key_concepts": (
                    "Split the middle term.\n"
                    "Factorise the expression.\n"
                    "Use the zero-product property."
                ),
                "worked_example": (
                    "x² + 5x + 6 = 0\n"
                    "(x + 2)(x + 3) = 0\n"
                    "x = -2 or x = -3."
                ),
            },
            {
                "name": "Quadratic Formula",
                "difficulty": 2,
                "explanation": (
                    "Quadratic equations can be solved using "
                    "the quadratic formula when factorisation "
                    "is difficult."
                ),
                "key_concepts": (
                    "For ax² + bx + c = 0:\n"
                    "x = (-b ± √(b² - 4ac)) / 2a."
                ),
                "worked_example": (
                    "For x² - 5x + 6 = 0:\n"
                    "a=1, b=-5, c=6.\n"
                    "Using the formula gives x=2 or x=3."
                ),
            },
            {
                "name": "Discriminant and Nature of Roots",
                "difficulty": 2,
                "explanation": (
                    "The discriminant determines the nature "
                    "of the roots of a quadratic equation."
                ),
                "key_concepts": (
                    "D = b² - 4ac.\n"
                    "D > 0: two distinct real roots.\n"
                    "D = 0: equal real roots.\n"
                    "D < 0: no real roots."
                ),
                "worked_example": (
                    "For x² - 4x + 4 = 0:\n"
                    "D = 16 - 16 = 0.\n"
                    "Therefore the roots are equal."
                ),
            },
            {
                "name": "Applications of Quadratic Equations",
                "difficulty": 3,
                "explanation": (
                    "Real-life situations involving areas, "
                    "numbers and dimensions can often be "
                    "represented using quadratic equations."
                ),
                "key_concepts": (
                    "Choose a variable.\n"
                    "Form the quadratic equation.\n"
                    "Solve it.\n"
                    "Reject impossible values if necessary."
                ),
                "worked_example": (
                    "If the product of two consecutive "
                    "positive integers is 56, then "
                    "x(x+1)=56, which gives x=7."
                ),
            },
        ],
    },

    5: {
        "chapter": "Arithmetic Progressions",
        "topics": [
            {
                "name": "Introduction to Arithmetic Progressions",
                "difficulty": 1,
                "explanation": (
                    "An arithmetic progression is a sequence "
                    "in which the difference between "
                    "consecutive terms is constant."
                ),
                "key_concepts": (
                    "First term = a.\n"
                    "Common difference = d.\n"
                    "General form: a, a+d, a+2d, ..."
                ),
                "worked_example": (
                    "2, 5, 8, 11, ... is an AP because "
                    "the common difference is 3."
                ),
            },
            {
                "name": "nth Term of an Arithmetic Progression",
                "difficulty": 2,
                "explanation": (
                    "The nth term formula is used to find "
                    "any required term of an arithmetic "
                    "progression."
                ),
                "key_concepts": (
                    "aₙ = a + (n - 1)d."
                ),
                "worked_example": (
                    "For 2,5,8,... the 10th term is "
                    "2 + 9(3) = 29."
                ),
            },
            {
                "name": "Sum of First n Terms",
                "difficulty": 2,
                "explanation": (
                    "The sum formula allows us to find the "
                    "sum of several terms of an AP directly."
                ),
                "key_concepts": (
                    "Sₙ = n/2[2a + (n-1)d]."
                ),
                "worked_example": (
                    "For 2,5,8,... the sum of first "
                    "4 terms is 2+5+8+11=26."
                ),
            },
            {
                "name": "Applications of Arithmetic Progressions",
                "difficulty": 3,
                "explanation": (
                    "Arithmetic progressions are useful for "
                    "situations involving regular increases "
                    "or decreases."
                ),
                "key_concepts": (
                    "Identify a and d.\n"
                    "Choose nth-term or sum formula.\n"
                    "Interpret the result."
                ),
                "worked_example": (
                    "If savings increase by ₹100 every month, "
                    "the monthly savings form an AP."
                ),
            },
        ],
    },

    6: {
        "chapter": "Triangles",
        "topics": [
            {
                "name": "Similar Figures and Similar Triangles",
                "difficulty": 1,
                "explanation": (
                    "Similar figures have the same shape, "
                    "while similar triangles have equal "
                    "corresponding angles and proportional "
                    "corresponding sides."
                ),
                "key_concepts": (
                    "Corresponding angles are equal.\n"
                    "Corresponding sides are proportional."
                ),
                "worked_example": (
                    "Triangles with sides 3,4,5 and 6,8,10 "
                    "have proportional corresponding sides."
                ),
            },
            {
                "name": "Basic Proportionality Theorem",
                "difficulty": 2,
                "explanation": (
                    "A line drawn parallel to one side of a "
                    "triangle divides the other two sides "
                    "in the same ratio."
                ),
                "key_concepts": (
                    "Also called Thales' theorem.\n"
                    "Parallel line produces proportional "
                    "segments."
                ),
                "worked_example": (
                    "If DE is parallel to BC in triangle ABC, "
                    "then AD/DB = AE/EC."
                ),
            },
            {
                "name": "Converse of Basic Proportionality Theorem",
                "difficulty": 2,
                "explanation": (
                    "If a line divides two sides of a "
                    "triangle in the same ratio, then that "
                    "line is parallel to the third side."
                ),
                "key_concepts": (
                    "Proportional division implies "
                    "parallelism."
                ),
                "worked_example": (
                    "If AD/DB = AE/EC, then DE is "
                    "parallel to BC."
                ),
            },
            {
                "name": "Criteria for Similarity of Triangles",
                "difficulty": 2,
                "explanation": (
                    "Triangles can be proved similar using "
                    "standard similarity criteria."
                ),
                "key_concepts": (
                    "AAA similarity.\n"
                    "SSS similarity.\n"
                    "SAS similarity."
                ),
                "worked_example": (
                    "If two corresponding angles of two "
                    "triangles are equal, the triangles "
                    "are similar by AAA."
                ),
            },
        ],
    },

    7: {
        "chapter": "Coordinate Geometry",
        "topics": [
            {
                "name": "Cartesian Coordinate System",
                "difficulty": 1,
                "explanation": (
                    "The Cartesian coordinate system locates "
                    "points using an x-coordinate and "
                    "a y-coordinate."
                ),
                "key_concepts": (
                    "Origin = (0,0).\n"
                    "x-axis is horizontal.\n"
                    "y-axis is vertical."
                ),
                "worked_example": (
                    "The point (3,2) is 3 units along "
                    "the x-axis and 2 units upward."
                ),
            },
            {
                "name": "Distance Formula",
                "difficulty": 2,
                "explanation": (
                    "The distance formula gives the length "
                    "between two points on a coordinate plane."
                ),
                "key_concepts": (
                    "d = √[(x₂-x₁)² + (y₂-y₁)²]."
                ),
                "worked_example": (
                    "Distance between (0,0) and (3,4) "
                    "is √(9+16)=5."
                ),
            },
            {
                "name": "Section and Midpoint Formula",
                "difficulty": 2,
                "explanation": (
                    "The section formula finds coordinates "
                    "of a point dividing a line segment. "
                    "The midpoint is a special case."
                ),
                "key_concepts": (
                    "Midpoint = "
                    "((x₁+x₂)/2, (y₁+y₂)/2).\n"
                    "Section formula is used for internal "
                    "division in a given ratio."
                ),
                "worked_example": (
                    "Midpoint of (2,4) and (6,8) "
                    "is (4,6)."
                ),
            },
        ],
    },

    8: {
        "chapter": "Introduction to Trigonometry",
        "topics": [
            {
                "name": "Trigonometric Ratios",
                "difficulty": 1,
                "explanation": (
                    "Trigonometric ratios relate the sides "
                    "of a right-angled triangle to an "
                    "acute angle."
                ),
                "key_concepts": (
                    "sin θ = opposite/hypotenuse.\n"
                    "cos θ = adjacent/hypotenuse.\n"
                    "tan θ = opposite/adjacent."
                ),
                "worked_example": (
                    "For a 3-4-5 triangle, if opposite=3 "
                    "and hypotenuse=5, sin θ=3/5."
                ),
            },
            {
                "name": "Trigonometric Ratios of Specific Angles",
                "difficulty": 2,
                "explanation": (
                    "Standard trigonometric values are used "
                    "for angles such as 0°, 30°, 45°, "
                    "60° and 90°."
                ),
                "key_concepts": (
                    "Learn standard values of sin, cos "
                    "and tan."
                ),
                "worked_example": (
                    "sin 30° = 1/2 and cos 60° = 1/2."
                ),
            },
            {
                "name": "Relationships Between Trigonometric Ratios",
                "difficulty": 2,
                "explanation": (
                    "Different trigonometric ratios are "
                    "related through reciprocal and "
                    "quotient relationships."
                ),
                "key_concepts": (
                    "tan θ = sin θ / cos θ.\n"
                    "cot θ = cos θ / sin θ."
                ),
                "worked_example": (
                    "If sin θ=3/5 and cos θ=4/5, "
                    "then tan θ=3/4."
                ),
            },
            {
                "name": "Trigonometric Identities",
                "difficulty": 3,
                "explanation": (
                    "A trigonometric identity is an "
                    "equation that is true for all valid "
                    "values of the angle."
                ),
                "key_concepts": (
                    "sin²θ + cos²θ = 1.\n"
                    "1 + tan²θ = sec²θ."
                ),
                "worked_example": (
                    "If sin θ=3/5 and cos θ=4/5, "
                    "sin²θ+cos²θ=9/25+16/25=1."
                ),
            },
        ],
    },

    9: {
        "chapter": "Some Applications of Trigonometry",
        "topics": [
            {
                "name": "Line of Sight",
                "difficulty": 1,
                "explanation": (
                    "The line of sight is the line joining "
                    "the observer's eye to the object "
                    "being viewed."
                ),
                "key_concepts": (
                    "Horizontal line.\n"
                    "Line of sight.\n"
                    "Reference angle."
                ),
                "worked_example": (
                    "Looking from the ground to the top "
                    "of a tower creates an angle with "
                    "the horizontal."
                ),
            },
            {
                "name": "Angles of Elevation and Depression",
                "difficulty": 2,
                "explanation": (
                    "An angle of elevation is measured "
                    "upward from the horizontal, while an "
                    "angle of depression is measured downward."
                ),
                "key_concepts": (
                    "Elevation: object above observer.\n"
                    "Depression: object below observer."
                ),
                "worked_example": (
                    "A person looking upward at the top "
                    "of a building observes an angle "
                    "of elevation."
                ),
            },
            {
                "name": "Heights and Distances",
                "difficulty": 3,
                "explanation": (
                    "Trigonometric ratios can determine "
                    "unknown heights and distances without "
                    "measuring them directly."
                ),
                "key_concepts": (
                    "Draw a right triangle.\n"
                    "Identify known sides and angle.\n"
                    "Choose the correct ratio."
                ),
                "worked_example": (
                    "If tan 45° = height/20 and tan45°=1, "
                    "the height is 20 m."
                ),
            },
        ],
    },

    10: {
        "chapter": "Circles",
        "topics": [
            {
                "name": "Tangent to a Circle",
                "difficulty": 1,
                "explanation": (
                    "A tangent touches a circle at exactly "
                    "one point, called the point of contact."
                ),
                "key_concepts": (
                    "Tangent.\n"
                    "Point of contact.\n"
                    "Radius."
                ),
                "worked_example": (
                    "A straight line touching a circle "
                    "only at P is tangent at P."
                ),
            },
            {
                "name": "Tangent and Radius Theorem",
                "difficulty": 2,
                "explanation": (
                    "The tangent at any point of a circle "
                    "is perpendicular to the radius through "
                    "the point of contact."
                ),
                "key_concepts": (
                    "Radius ⟂ tangent at point of contact."
                ),
                "worked_example": (
                    "If OP is a radius and PT is tangent "
                    "at P, angle OPT is 90°."
                ),
            },
            {
                "name": "Tangents from an External Point",
                "difficulty": 2,
                "explanation": (
                    "The lengths of two tangents drawn "
                    "from the same external point to a "
                    "circle are equal."
                ),
                "key_concepts": (
                    "If PA and PB are tangents from P, "
                    "then PA = PB."
                ),
                "worked_example": (
                    "If PA=8 cm, then another tangent PB "
                    "from the same point also has length "
                    "8 cm."
                ),
            },
        ],
    },

    11: {
        "chapter": "Areas Related to Circles",
        "topics": [
            {
                "name": "Area and Circumference of a Circle",
                "difficulty": 1,
                "explanation": (
                    "The circumference and area of a circle "
                    "depend on its radius."
                ),
                "key_concepts": (
                    "Circumference = 2πr.\n"
                    "Area = πr²."
                ),
                "worked_example": (
                    "For r=7 cm, area=49π cm²."
                ),
            },
            {
                "name": "Area of a Sector",
                "difficulty": 2,
                "explanation": (
                    "A sector is the region bounded by two "
                    "radii and the corresponding arc."
                ),
                "key_concepts": (
                    "Sector area = θ/360 × πr²."
                ),
                "worked_example": (
                    "A 90° sector occupies one quarter "
                    "of the area of the circle."
                ),
            },
            {
                "name": "Area of a Segment",
                "difficulty": 2,
                "explanation": (
                    "A segment is the region between a "
                    "chord and its corresponding arc."
                ),
                "key_concepts": (
                    "Segment area = sector area "
                    "- triangle area."
                ),
                "worked_example": (
                    "Find the sector area first, then "
                    "subtract the area of the triangle."
                ),
            },
            {
                "name": "Combined Plane Figures",
                "difficulty": 3,
                "explanation": (
                    "Areas of combined figures can be found "
                    "by adding or subtracting familiar "
                    "geometrical areas."
                ),
                "key_concepts": (
                    "Break the figure into simple shapes.\n"
                    "Add required regions.\n"
                    "Subtract excluded regions."
                ),
                "worked_example": (
                    "A shaded region may be found by "
                    "subtracting a circle from a rectangle."
                ),
            },
        ],
    },

    12: {
        "chapter": "Surface Areas and Volumes",
        "topics": [
            {
                "name": "Surface Areas of Combined Solids",
                "difficulty": 2,
                "explanation": (
                    "When solids are combined, only the "
                    "exposed surfaces contribute to the "
                    "external surface area."
                ),
                "key_concepts": (
                    "Identify exposed surfaces.\n"
                    "Do not count joined surfaces."
                ),
                "worked_example": (
                    "For a hemisphere mounted on a cylinder, "
                    "the joined circular face is not exposed."
                ),
            },
            {
                "name": "Volumes of Combined Solids",
                "difficulty": 2,
                "explanation": (
                    "The total volume of a combined solid "
                    "is obtained by adding or subtracting "
                    "the volumes of its component solids."
                ),
                "key_concepts": (
                    "Cylinder volume = πr²h.\n"
                    "Cone volume = 1/3 πr²h.\n"
                    "Sphere volume = 4/3 πr³."
                ),
                "worked_example": (
                    "For a cone placed on a cylinder, "
                    "total volume = cylinder volume "
                    "+ cone volume."
                ),
            },
            {
                "name": "Conversion of Solids",
                "difficulty": 3,
                "explanation": (
                    "When one solid is melted and recast "
                    "into another shape, the volume remains "
                    "unchanged."
                ),
                "key_concepts": (
                    "Original volume = new volume."
                ),
                "worked_example": (
                    "A metal sphere melted into smaller "
                    "spheres preserves total volume."
                ),
            },
        ],
    },

    13: {
        "chapter": "Statistics",
        "topics": [
            {
                "name": "Mean of Grouped Data",
                "difficulty": 2,
                "explanation": (
                    "The mean of grouped observations can "
                    "be calculated using class marks and "
                    "frequencies."
                ),
                "key_concepts": (
                    "Direct method.\n"
                    "Assumed mean method.\n"
                    "Step-deviation method."
                ),
                "worked_example": (
                    "Multiply each class mark by its "
                    "frequency and divide the total by "
                    "the total frequency."
                ),
            },
            {
                "name": "Mode of Grouped Data",
                "difficulty": 2,
                "explanation": (
                    "The mode represents the value associated "
                    "with the highest frequency in grouped "
                    "data."
                ),
                "key_concepts": (
                    "Identify modal class.\n"
                    "Use the grouped-data mode formula."
                ),
                "worked_example": (
                    "The class interval having the highest "
                    "frequency is the modal class."
                ),
            },
            {
                "name": "Median of Grouped Data",
                "difficulty": 2,
                "explanation": (
                    "The median divides an ordered data set "
                    "into two equal parts."
                ),
                "key_concepts": (
                    "Find cumulative frequencies.\n"
                    "Locate N/2.\n"
                    "Identify median class."
                ),
                "worked_example": (
                    "The median class contains the "
                    "observation corresponding to N/2."
                ),
            },
            {
                "name": "Cumulative Frequency",
                "difficulty": 3,
                "explanation": (
                    "Cumulative frequency is the running "
                    "total of frequencies across class "
                    "intervals."
                ),
                "key_concepts": (
                    "Add frequencies successively.\n"
                    "Useful for locating the median."
                ),
                "worked_example": (
                    "For frequencies 3,5,4, cumulative "
                    "frequencies are 3,8,12."
                ),
            },
        ],
    },

    14: {
        "chapter": "Probability",
        "topics": [
            {
                "name": "Introduction to Probability",
                "difficulty": 1,
                "explanation": (
                    "Probability measures how likely an "
                    "event is to occur."
                ),
                "key_concepts": (
                    "Probability ranges from 0 to 1.\n"
                    "Impossible event = 0.\n"
                    "Certain event = 1."
                ),
                "worked_example": (
                    "For a fair coin, probability of "
                    "heads is 1/2."
                ),
            },
            {
                "name": "Classical Probability",
                "difficulty": 2,
                "explanation": (
                    "For equally likely outcomes, probability "
                    "is calculated using favourable outcomes "
                    "and total possible outcomes."
                ),
                "key_concepts": (
                    "P(E) = favourable outcomes "
                    "/ total outcomes."
                ),
                "worked_example": (
                    "For a fair die, P(6)=1/6."
                ),
            },
            {
                "name": "Probability of Simple Events",
                "difficulty": 2,
                "explanation": (
                    "Simple probability problems involve "
                    "coins, dice, cards and other equally "
                    "likely outcomes."
                ),
                "key_concepts": (
                    "List the sample space.\n"
                    "Count favourable outcomes.\n"
                    "Apply the probability formula."
                ),
                "worked_example": (
                    "For a die, even outcomes are 2,4,6, "
                    "so P(even)=3/6=1/2."
                ),
            },
        ],
    },
}


class Command(BaseCommand):
    help = (
        "Bulk seed KSEAB SSLC Class 10 Mathematics "
        "topics and learning content for Chapters 4-14."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Bulk seeding KSEAB Mathematics..."
            )
        )

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

        except (
            Board.DoesNotExist,
            AcademicYear.DoesNotExist,
            Grade.DoesNotExist,
            Subject.DoesNotExist,
        ):
            self.stdout.write(
                self.style.ERROR(
                    "KSEAB Mathematics curriculum "
                    "was not found. Run seed_kseab first."
                )
            )
            return

        total_topics = 0
        total_learning_content = 0

        for chapter_number, chapter_data in (
            MATHEMATICS_DATA.items()
        ):

            try:
                chapter = Chapter.objects.get(
                    subject=mathematics,
                    chapter_number=chapter_number,
                    name=chapter_data["chapter"],
                )

            except Chapter.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Chapter {chapter_number} "
                        f"'{chapter_data['chapter']}' "
                        "was not found."
                    )
                )
                continue

            self.stdout.write("")
            self.stdout.write(
                self.style.MIGRATE_LABEL(
                    f"Chapter {chapter_number}: "
                    f"{chapter.name}"
                )
            )

            for topic_data in chapter_data["topics"]:

                topic, created = Topic.objects.update_or_create(
                    chapter=chapter,
                    name=topic_data["name"],
                    defaults={
                        "description": (
                            topic_data["explanation"]
                        ),
                        "difficulty": (
                            topic_data["difficulty"]
                        ),
                    },
                )

                LearningContent.objects.update_or_create(
                    topic=topic,
                    defaults={
                        "explanation": (
                            topic_data["explanation"]
                        ),
                        "key_concepts": (
                            topic_data["key_concepts"]
                        ),
                        "easy_method": (
                            "Step 1: Identify the information "
                            "given in the problem.\n"
                            "Step 2: Recall the relevant "
                            "definition, theorem or formula.\n"
                            "Step 3: Substitute the known "
                            "values carefully.\n"
                            "Step 4: Simplify step by step.\n"
                            "Step 5: Check the final answer."
                        ),
                        "worked_example": (
                            topic_data["worked_example"]
                        ),
                        "common_mistakes": (
                            "1. Using the wrong formula or "
                            "theorem.\n"
                            "2. Missing signs or units.\n"
                            "3. Substituting values in the "
                            "wrong positions.\n"
                            "4. Skipping the final answer "
                            "check."
                        ),
                    },
                )

                status_text = (
                    "CREATED"
                    if created
                    else "UPDATED"
                )

                self.stdout.write(
                    f"  [{status_text}] {topic.name}"
                )

                total_topics += 1
                total_learning_content += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "KSEAB Mathematics bulk curriculum "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Processed topics: {total_topics}"
        )

        self.stdout.write(
            "Processed learning contents: "
            f"{total_learning_content}"
        )

        self.stdout.write(
            "Chapters 1-3 were preserved."
        )