from django.core.management.base import BaseCommand
from django.db import transaction

from courses.data.kseab_second_language_english import (
    ENGLISH_SECOND_LANGUAGE_DATA,
)

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
        "Bulk seed KSEAB SSLC Second Language English "
        "literature curriculum and learning content."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Bulk seeding Second Language English..."
            )
        )

        # =========================================================
        # LOCATE SECOND LANGUAGE ENGLISH
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

            english = Subject.objects.get(
                grade=grade,
                name="English",
                language="English",
                subject_type="second_language",
            )

        except (
            Board.DoesNotExist,
            AcademicYear.DoesNotExist,
            Grade.DoesNotExist,
            Subject.DoesNotExist,
        ):
            self.stdout.write(
                self.style.ERROR(
                    "KSEAB Second Language English "
                    "subject was not found. "
                    "Run seed_kseab first."
                )
            )
            return

        total_topics = 0
        total_content = 0

        # =========================================================
        # CREATE SECTIONS AND LESSONS
        # =========================================================

        for chapter_number, data in (
            ENGLISH_SECOND_LANGUAGE_DATA.items()
        ):

            chapter, chapter_created = (
                Chapter.objects.update_or_create(
                    subject=english,
                    chapter_number=chapter_number,
                    defaults={
                        "name": data["chapter"],
                        "description": (
                            "KSEAB SSLC Second Language English - "
                            f"{data['chapter']}"
                        ),
                    },
                )
            )

            chapter_state = (
                "CREATED"
                if chapter_created
                else "UPDATED"
            )

            self.stdout.write("")

            self.stdout.write(
                self.style.MIGRATE_LABEL(
                    f"[{chapter_state}] "
                    f"Section {chapter_number}: "
                    f"{chapter.name}"
                )
            )

            for index, topic_name in enumerate(
                data["topics"],
                start=1,
            ):

                difficulty = self._difficulty(
                    index=index,
                    total=len(data["topics"]),
                )

                topic, created = (
                    Topic.objects.update_or_create(
                        chapter=chapter,
                        name=topic_name,
                        defaults={
                            "description": (
                                "KSEAB SSLC Second Language "
                                f"English lesson: {topic_name}"
                            ),
                            "difficulty": difficulty,
                        },
                    )
                )

                LearningContent.objects.update_or_create(
                    topic=topic,
                    defaults={
                        "explanation": (
                            f"Study '{topic_name}' by understanding "
                            "its central idea, important events, "
                            "characters, themes and language."
                        ),

                        "key_concepts": (
                            f"Lesson: {topic_name}\n"
                            f"Section: {chapter.name}\n"
                            "Central idea, important details, "
                            "characters or poetic ideas, vocabulary "
                            "and text-based comprehension."
                        ),

                        "easy_method": (
                            "Step 1: Read the lesson carefully.\n"
                            "Step 2: Identify difficult words and "
                            "their meanings.\n"
                            "Step 3: Find the main idea or theme.\n"
                            "Step 4: Note important characters, "
                            "events or poetic ideas.\n"
                            "Step 5: Answer text-based questions "
                            "and revise the key points."
                        ),

                        "worked_example": (
                            f"Practice: Identify the central idea of "
                            f"'{topic_name}' and write two important "
                            "points from the text."
                        ),

                        "common_mistakes": (
                            "1. Memorising answers without "
                            "understanding the text.\n"
                            "2. Writing details unrelated to the "
                            "question.\n"
                            "3. Ignoring important vocabulary and "
                            "context.\n"
                            "4. Making avoidable grammar and "
                            "spelling mistakes."
                        ),
                    },
                )

                state = (
                    "CREATED"
                    if created
                    else "UPDATED"
                )

                self.stdout.write(
                    f"  [{state}] "
                    f"{index}. {topic.name}"
                )

                total_topics += 1
                total_content += 1

        # =========================================================
        # SUMMARY
        # =========================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Second Language English literature "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Sections: "
            f"{len(ENGLISH_SECOND_LANGUAGE_DATA)}"
        )

        self.stdout.write(
            f"Lessons: {total_topics}"
        )

        self.stdout.write(
            f"Learning contents: {total_content}"
        )

    def _difficulty(
        self,
        index,
        total,
    ):

        if index <= 2:
            return 1

        if index == total:
            return 3

        return 2