from django.core.management.base import BaseCommand
from django.db import transaction

from courses.data.kseab_first_language_kannada import (
    KANNADA_FIRST_LANGUAGE_DATA,
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
        "Bulk seed KSEAB SSLC First Language Kannada "
        "chapters, lessons and baseline learning content."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Bulk seeding First Language Kannada..."
            )
        )

        # =========================================================
        # LOCATE KSEAB FIRST LANGUAGE KANNADA
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

            kannada = Subject.objects.get(
                grade=grade,
                name="Kannada",
                language="Kannada",
                subject_type="first_language",
            )

        except (
            Board.DoesNotExist,
            AcademicYear.DoesNotExist,
            Grade.DoesNotExist,
            Subject.DoesNotExist,
        ):
            self.stdout.write(
                self.style.ERROR(
                    "KSEAB First Language Kannada "
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
            KANNADA_FIRST_LANGUAGE_DATA.items()
        ):

            chapter, chapter_created = (
                Chapter.objects.update_or_create(
                    subject=kannada,
                    chapter_number=chapter_number,
                    defaults={
                        "name": data["chapter"],
                        "description": (
                            "KSEAB SSLC First Language Kannada - "
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
                                "KSEAB SSLC First Language "
                                f"Kannada lesson: {topic_name}"
                            ),
                            "difficulty": difficulty,
                        },
                    )
                )

                LearningContent.objects.update_or_create(
                    topic=topic,
                    defaults={
                        "explanation": (
                            f"'{topic_name}' ಪಾಠವನ್ನು "
                            "ಅರ್ಥೈಸಿಕೊಂಡು ಓದುವುದು, ಪ್ರಮುಖ "
                            "ವಿಚಾರಗಳನ್ನು ಗುರುತಿಸುವುದು ಹಾಗೂ "
                            "ಪಠ್ಯದ ಅರ್ಥಗ್ರಹಣವನ್ನು ಬೆಳೆಸುವುದು."
                        ),

                        "key_concepts": (
                            f"ಪಾಠ: {topic_name}\n"
                            f"ವಿಭಾಗ: {chapter.name}\n"
                            "ಮುಖ್ಯ ವಿಚಾರಗಳು, ಪದಾರ್ಥಗಳು, "
                            "ಪಾತ್ರಗಳು ಅಥವಾ ಕಾವ್ಯಾರ್ಥ ಮತ್ತು "
                            "ಪಠ್ಯಾಧಾರಿತ ಪ್ರಶ್ನೆಗಳ ಅಧ್ಯಯನ."
                        ),

                        "easy_method": (
                            "ಹಂತ 1: ಪಾಠವನ್ನು ಸಂಪೂರ್ಣವಾಗಿ ಓದಿ.\n"
                            "ಹಂತ 2: ಕಠಿಣ ಪದಗಳ ಅರ್ಥ ತಿಳಿಯಿರಿ.\n"
                            "ಹಂತ 3: ಮುಖ್ಯ ವಿಚಾರಗಳನ್ನು ಗುರುತಿಸಿ.\n"
                            "ಹಂತ 4: ಪಠ್ಯಾಧಾರಿತ ಪ್ರಶ್ನೆಗಳಿಗೆ "
                            "ಉತ್ತರಿಸಿ.\n"
                            "ಹಂತ 5: ಮುಖ್ಯ ಅಂಶಗಳನ್ನು ಪುನರವಲೋಕಿಸಿ."
                        ),

                        "worked_example": (
                            f"ಅಭ್ಯಾಸ: '{topic_name}' ಪಾಠದ "
                            "ಮುಖ್ಯ ಆಶಯವನ್ನು ಗುರುತಿಸಿ ಮತ್ತು "
                            "ಪಠ್ಯದಿಂದ ಎರಡು ಮುಖ್ಯ ಅಂಶಗಳನ್ನು "
                            "ಬರೆಯಿರಿ."
                        ),

                        "common_mistakes": (
                            "1. ಪಾಠವನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳದೆ "
                            "ಕೇವಲ ಕಂಠಪಾಠ ಮಾಡುವುದು.\n"
                            "2. ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸದ ಉತ್ತರ "
                            "ಬರೆಯುವುದು.\n"
                            "3. ಪ್ರಮುಖ ಪದಗಳು ಮತ್ತು ಅರ್ಥಗಳನ್ನು "
                            "ಗಮನಿಸದಿರುವುದು.\n"
                            "4. ಕಾಗುಣಿತ ಮತ್ತು ವ್ಯಾಕರಣದ "
                            "ತಪ್ಪುಗಳನ್ನು ನಿರ್ಲಕ್ಷಿಸುವುದು."
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
                "First Language Kannada curriculum "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Sections: "
            f"{len(KANNADA_FIRST_LANGUAGE_DATA)}"
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