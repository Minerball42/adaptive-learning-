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
    help = (
        "Seed Karnataka KSEAB SSLC Class 10 "
        "curriculum and subject structure"
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Setting up KSEAB SSLC Class 10..."
            )
        )

        # =========================================================
        # 1. BOARD
        # =========================================================

        board, created = Board.objects.update_or_create(
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
            created,
        )

        # =========================================================
        # 2. ACADEMIC YEAR
        # =========================================================

        academic_year, created = (
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
            created,
        )

        # =========================================================
        # 3. GRADE
        # =========================================================

        grade, created = Grade.objects.update_or_create(
            academic_year=academic_year,
            name="SSLC Class 10",
            defaults={
                "level": 10,
                "description": (
                    "KSEAB Karnataka SSLC Class 10"
                ),
            },
        )

        self._print_status(
            "Grade",
            grade,
            created,
        )

        # =========================================================
        # 4. CORE SUBJECTS
        # =========================================================

        mathematics = self._create_subject(
            grade=grade,
            name="Mathematics",
            description=(
                "KSEAB SSLC Class 10 Mathematics"
            ),
            language="English",
            subject_type="core",
            is_optional=False,
            display_order=1,
        )

        science = self._create_subject(
            grade=grade,
            name="Science",
            description=(
                "KSEAB SSLC Class 10 Science"
            ),
            language="English",
            subject_type="core",
            is_optional=False,
            display_order=2,
        )

        social_science = self._create_subject(
            grade=grade,
            name="Social Science",
            description=(
                "KSEAB SSLC Class 10 Social Science"
            ),
            language="English",
            subject_type="core",
            is_optional=False,
            display_order=3,
        )

        # =========================================================
        # 5. FIRST LANGUAGE SUBJECTS
        # =========================================================

        first_languages = [
            "Kannada",
            "English",
            "Hindi",
            "Sanskrit",
            "Telugu",
            "Tamil",
            "Marathi",
            "Urdu",
        ]

        for index, language_name in enumerate(
            first_languages,
            start=10,
        ):
            self._create_subject(
                grade=grade,
                name=language_name,
                description=(
                    f"KSEAB SSLC First Language "
                    f"{language_name}"
                ),
                language=language_name,
                subject_type="first_language",
                is_optional=False,
                display_order=index,
            )

        # =========================================================
        # 6. SECOND LANGUAGE SUBJECTS
        # =========================================================

        second_languages = [
            "Kannada",
            "English",
        ]

        for index, language_name in enumerate(
            second_languages,
            start=30,
        ):
            self._create_subject(
                grade=grade,
                name=language_name,
                description=(
                    f"KSEAB SSLC Second Language "
                    f"{language_name}"
                ),
                language=language_name,
                subject_type="second_language",
                is_optional=False,
                display_order=index,
            )

        # =========================================================
        # 7. THIRD LANGUAGE SUBJECTS
        # =========================================================

        third_languages = [
            "Hindi",
            "Kannada",
            "English",
            "Arabic",
            "Urdu",
            "Sanskrit",
            "Konkani",
            "Tulu",
        ]

        for index, language_name in enumerate(
            third_languages,
            start=40,
        ):
            self._create_subject(
                grade=grade,
                name=language_name,
                description=(
                    f"KSEAB SSLC Third Language "
                    f"{language_name}"
                ),
                language=language_name,
                subject_type="third_language",
                is_optional=False,
                display_order=index,
            )

        # =========================================================
        # 8. NSQF / SKILL SUBJECTS
        # =========================================================

        skill_subjects = [
            "Information Technology",
            "Retail",
            "Automobile",
            "Beauty & Wellness",
            "Electronics & Hardware",
        ]

        for index, subject_name in enumerate(
            skill_subjects,
            start=60,
        ):
            self._create_subject(
                grade=grade,
                name=subject_name,
                description=(
                    f"KSEAB SSLC NSQF / Skill Subject - "
                    f"{subject_name}"
                ),
                language="English",
                subject_type="optional",
                is_optional=True,
                display_order=index,
            )

        # =========================================================
        # 9. MATHEMATICS CHAPTERS
        # =========================================================

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

        mathematics_objects = {}

        for number, name in mathematics_chapters:

            chapter = self._create_chapter(
                subject=mathematics,
                chapter_number=number,
                name=name,
            )

            mathematics_objects[number] = chapter

        # =========================================================
        # 10. SCIENCE CHAPTERS
        # =========================================================

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

        for number, name in science_chapters:

            self._create_chapter(
                subject=science,
                chapter_number=number,
                name=name,
            )

        # =========================================================
        # 11. SOCIAL SCIENCE CHAPTERS
        # =========================================================

        social_science_chapters = [
            # History
            (
                1,
                "The Advent of Europeans to India",
            ),
            (
                2,
                "The Extension of the British Rule",
            ),
            (
                3,
                "The Impact of British Rule in India",
            ),
            (
                4,
                (
                    "Opposition to British Rule in "
                    "Karnataka and Wodiyars of Mysore"
                ),
            ),
            (
                5,
                (
                    "Social and Religious "
                    "Reformation Movements"
                ),
            ),
            (
                6,
                (
                    "The First War of Indian "
                    "Independence (1857)"
                ),
            ),
            (
                7,
                "The Freedom Struggle",
            ),
            (
                8,
                "India After Independence",
            ),
            (
                9,
                "World Wars and India's Role",
            ),

            # Political Science
            (
                10,
                "Public Administration - An Introduction",
            ),
            (
                11,
                "Challenges of India and Their Remedies",
            ),
            (
                12,
                (
                    "India's Foreign Policy "
                    "and Global Challenges"
                ),
            ),
            (
                13,
                "World Organizations",
            ),

            # Sociology
            (
                14,
                "Social Stratification",
            ),
            (
                15,
                "Work and Economic Life",
            ),
            (
                16,
                "Collective Behaviour and Protests",
            ),
            (
                17,
                "Social Challenges",
            ),

            # Geography
            (
                18,
                (
                    "India - Geographical Position "
                    "and Physical Features"
                ),
            ),
            (
                19,
                "India - Seasons",
            ),
            (
                20,
                "India - Soils",
            ),
            (
                21,
                "India - Forest Resources",
            ),
            (
                22,
                "India - Water Resources",
            ),
            (
                23,
                "India - Land Use and Agriculture",
            ),
            (
                24,
                "India - Mineral and Power Resources",
            ),
            (
                25,
                "India - Transport and Communication",
            ),
            (
                26,
                "India - Major Industries",
            ),
            (
                27,
                "India - Natural Disasters",
            ),

            # Economics
            (
                28,
                "Economy and Government",
            ),
            (
                29,
                "Rural Development",
            ),
            (
                30,
                "Public Finance and Budget",
            ),

            # Business Studies
            (
                31,
                "Bank Transactions",
            ),
            (
                32,
                "Entrepreneurship",
            ),
            (
                33,
                "Consumer Education and Protection",
            ),
        ]

        for number, name in social_science_chapters:

            self._create_chapter(
                subject=social_science,
                chapter_number=number,
                name=name,
            )

        # =========================================================
        # 12. REAL NUMBERS TOPICS
        # =========================================================

        real_numbers = mathematics_objects[1]

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

            topic, created = (
                Topic.objects.update_or_create(
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
            )

            self._print_status(
                "Topic",
                topic,
                created,
            )

        # =========================================================
        # SUMMARY
        # =========================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "KSEAB curriculum structure "
                "seeded successfully."
            )
        )

        self.stdout.write("")

        self.stdout.write(
            f"Board: {board.name}"
        )

        self.stdout.write(
            f"Academic Year: "
            f"{academic_year.name}"
        )

        self.stdout.write(
            f"Grade: {grade.name}"
        )

        self.stdout.write(
            f"Total Subjects: "
            f"{grade.subjects.count()}"
        )

        self.stdout.write(
            "Core Subjects: "
            f"{grade.subjects.filter(
                subject_type='core'
            ).count()}"
        )

        self.stdout.write(
            "First Languages: "
            f"{grade.subjects.filter(
                subject_type='first_language'
            ).count()}"
        )

        self.stdout.write(
            "Second Languages: "
            f"{grade.subjects.filter(
                subject_type='second_language'
            ).count()}"
        )

        self.stdout.write(
            "Third Languages: "
            f"{grade.subjects.filter(
                subject_type='third_language'
            ).count()}"
        )

        self.stdout.write(
            "Optional / Skill Subjects: "
            f"{grade.subjects.filter(
                subject_type='optional'
            ).count()}"
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

    # =============================================================
    # HELPERS
    # =============================================================

    def _create_subject(
        self,
        grade,
        name,
        description,
        language,
        subject_type,
        is_optional,
        display_order,
    ):

        subject, created = (
            Subject.objects.update_or_create(
                grade=grade,
                name=name,
                subject_type=subject_type,
                language=language,
                defaults={
                    "description": description,
                    "is_optional": is_optional,
                    "display_order": display_order,
                },
            )
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

        chapter, created = (
            Chapter.objects.update_or_create(
                subject=subject,
                chapter_number=chapter_number,
                defaults={
                    "name": name,
                    "description": "",
                },
            )
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

            object_status = (
                self.style.SUCCESS(
                    "CREATED"
                )
            )

        else:

            object_status = (
                self.style.WARNING(
                    "UPDATED"
                )
            )

        self.stdout.write(
            f"[{object_status}] "
            f"{object_type}: {obj}"
        )