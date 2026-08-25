from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import (
    Board,
    AcademicYear,
    Grade,
    Subject,
    Chapter,
    Topic,
)


class Command(BaseCommand):
    help = "Seed Karnataka KSEAB SSLC Class 10 curriculum"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Setting up Karnataka SSLC curriculum..."
            )
        )

        # ---------------------------------------------------------
        # 1. BOARD
        # ---------------------------------------------------------

        board, board_created = Board.objects.update_or_create(
            code="KSEAB",
            defaults={
                "name": (
                    "Karnataka School Examination "
                    "and Assessment Board"
                ),
                "state": "Karnataka",
                "country": "India",
                "is_active": True,
            },
        )

        self._print_status(
            "Board",
            board,
            board_created,
        )

        # ---------------------------------------------------------
        # 2. ACADEMIC YEAR
        # ---------------------------------------------------------

        academic_year, year_created = (
            AcademicYear.objects.update_or_create(
                board=board,
                name="2026-27",
                defaults={
                    "is_active": True,
                },
            )
        )

        self._print_status(
            "Academic Year",
            academic_year,
            year_created,
        )

        # ---------------------------------------------------------
        # 3. GRADE
        # ---------------------------------------------------------

        grade, grade_created = Grade.objects.update_or_create(
            academic_year=academic_year,
            name="SSLC Class 10",
            defaults={
                "level": 10,
                "description": (
                    "Karnataka State Board "
                    "SSLC Class 10"
                ),
            },
        )

        self._print_status(
            "Grade",
            grade,
            grade_created,
        )

        # ---------------------------------------------------------
        # 4. SUBJECTS
        # ---------------------------------------------------------

        mathematics = self._create_subject(
            grade=grade,
            name="Mathematics",
            description=(
                "Karnataka SSLC Class 10 Mathematics"
            ),
            language="English",
        )

        science = self._create_subject(
            grade=grade,
            name="Science",
            description=(
                "Karnataka SSLC Class 10 Science"
            ),
            language="English",
        )

        social_science = self._create_subject(
            grade=grade,
            name="Social Science",
            description=(
                "Karnataka SSLC Class 10 Social Science"
            ),
            language="English",
        )

        # ---------------------------------------------------------
        # 5. MATHEMATICS CHAPTERS
        # ---------------------------------------------------------

        mathematics_chapters = [
            (1, "Real Numbers"),
            (2, "Polynomials"),
            (
                3,
                "Pair of Linear Equations in Two Variables",
            ),
            (4, "Quadratic Equations"),
            (5, "Arithmetic Progressions"),
            (6, "Triangles"),
            (7, "Coordinate Geometry"),
            (8, "Introduction to Trigonometry"),
            (
                9,
                "Some Applications of Trigonometry",
            ),
            (10, "Circles"),
            (11, "Areas Related to Circles"),
            (12, "Surface Areas and Volumes"),
            (13, "Statistics"),
            (14, "Probability"),
        ]

        maths_chapter_objects = {}

        for chapter_number, chapter_name in mathematics_chapters:
            chapter = self._create_chapter(
                subject=mathematics,
                chapter_number=chapter_number,
                name=chapter_name,
            )

            maths_chapter_objects[
                chapter_number
            ] = chapter

        # ---------------------------------------------------------
        # 6. SCIENCE CHAPTERS
        # ---------------------------------------------------------

        science_chapters = [
            (
                1,
                "Chemical Reactions and Equations",
            ),
            (
                2,
                "Acids, Bases and Salts",
            ),
            (
                3,
                "Metals and Non-metals",
            ),
            (
                4,
                "Carbon and Its Compounds",
            ),
            (
                5,
                "Life Processes",
            ),
            (
                6,
                "Control and Coordination",
            ),
            (
                7,
                "How Do Organisms Reproduce?",
            ),
            (
                8,
                "Heredity",
            ),
            (
                9,
                "Light - Reflection and Refraction",
            ),
            (
                10,
                "The Human Eye and the Colourful World",
            ),
            (
                11,
                "Electricity",
            ),
            (
                12,
                "Magnetic Effects of Electric Current",
            ),
            (
                13,
                "Our Environment",
            ),
        ]

        for chapter_number, chapter_name in science_chapters:
            self._create_chapter(
                subject=science,
                chapter_number=chapter_number,
                name=chapter_name,
            )

        # ---------------------------------------------------------
        # 7. REAL NUMBERS TOPICS
        # ---------------------------------------------------------
        #
        # We are initially building ONE complete chapter.
        # Real Numbers will be our first adaptive-learning
        # demonstration chapter.
        # ---------------------------------------------------------

        real_numbers = maths_chapter_objects[1]

        real_number_topics = [
            {
                "name": "Introduction to Real Numbers",
                "description": (
                    "Introduction and revision of "
                    "real-number concepts."
                ),
                "difficulty": 1,
            },
            {
                "name": (
                    "Fundamental Theorem of Arithmetic"
                ),
                "description": (
                    "Prime factorisation and the "
                    "Fundamental Theorem of Arithmetic."
                ),
                "difficulty": 2,
            },
            {
                "name": "Revisiting Irrational Numbers",
                "description": (
                    "Understanding and proving properties "
                    "of irrational numbers."
                ),
                "difficulty": 2,
            },
        ]

        for topic_data in real_number_topics:
            topic, created = Topic.objects.update_or_create(
                chapter=real_numbers,
                name=topic_data["name"],
                defaults={
                    "description": (
                        topic_data["description"]
                    ),
                    "difficulty": (
                        topic_data["difficulty"]
                    ),
                },
            )

            self._print_status(
                "Topic",
                topic,
                created,
            )

        # ---------------------------------------------------------
        # SUMMARY
        # ---------------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "KSEAB curriculum seeded successfully."
            )
        )

        self.stdout.write("")
        self.stdout.write(
            f"Board: {board.name}"
        )

        self.stdout.write(
            f"Academic Year: {academic_year.name}"
        )

        self.stdout.write(
            f"Grade: {grade.name}"
        )

        self.stdout.write(
            f"Subjects: {grade.subjects.count()}"
        )

        self.stdout.write(
            f"Mathematics Chapters: "
            f"{mathematics.chapters.count()}"
        )

        self.stdout.write(
            f"Science Chapters: "
            f"{science.chapters.count()}"
        )

        self.stdout.write(
            f"Social Science Chapters: "
            f"{social_science.chapters.count()}"
        )

        self.stdout.write(
            f"Real Numbers Topics: "
            f"{real_numbers.topics.count()}"
        )

    # -------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------

    def _create_subject(
        self,
        grade,
        name,
        description,
        language,
    ):
        subject, created = Subject.objects.update_or_create(
            grade=grade,
            name=name,
            defaults={
                "description": description,
                "language": language,
            },
        )

        self._print_status(
            "Subject",
            subject,
            created,
        )

        return subject

    def _create_chapter(
        self,
        subject,
        chapter_number,
        name,
    ):
        chapter, created = Chapter.objects.update_or_create(
            subject=subject,
            chapter_number=chapter_number,
            defaults={
                "name": name,
                "description": "",
            },
        )

        self._print_status(
            "Chapter",
            chapter,
            created,
        )

        return chapter

    def _print_status(
        self,
        object_type,
        obj,
        created,
    ):
        if created:
            status = self.style.SUCCESS(
                "CREATED"
            )
        else:
            status = self.style.WARNING(
                "UPDATED"
            )

        self.stdout.write(
            f"[{status}] {object_type}: {obj}"
        )