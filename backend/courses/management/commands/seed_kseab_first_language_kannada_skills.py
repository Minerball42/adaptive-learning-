from django.core.management.base import BaseCommand
from django.db import transaction

from courses.data.kseab_first_language_kannada_skills import (
    KANNADA_FIRST_LANGUAGE_SKILLS,
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
        "Seed KSEAB SSLC First Language Kannada "
        "grammar, writing and comprehension skills."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding Kannada language skills..."
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
                    "First Language Kannada subject "
                    "was not found."
                )
            )
            return

        total_topics = 0
        total_content = 0

        for chapter_number, data in (
            KANNADA_FIRST_LANGUAGE_SKILLS.items()
        ):

            chapter, chapter_created = (
                Chapter.objects.update_or_create(
                    subject=kannada,
                    chapter_number=chapter_number,
                    defaults={
                        "name": data["chapter"],
                        "description": (
                            "KSEAB SSLC First Language "
                            f"Kannada - {data['chapter']}"
                        ),
                    },
                )
            )

            state = (
                "CREATED"
                if chapter_created
                else "UPDATED"
            )

            self.stdout.write("")
            self.stdout.write(
                self.style.MIGRATE_LABEL(
                    f"[{state}] Section "
                    f"{chapter_number}: {chapter.name}"
                )
            )

            for item in data["topics"]:

                topic, created = (
                    Topic.objects.update_or_create(
                        chapter=chapter,
                        name=item["name"],
                        defaults={
                            "description": (
                                item["explanation"]
                            ),
                            "difficulty": (
                                item["difficulty"]
                            ),
                        },
                    )
                )

                LearningContent.objects.update_or_create(
                    topic=topic,
                    defaults={
                        "explanation": (
                            item["explanation"]
                        ),

                        "key_concepts": (
                            f"ವಿಷಯ: {item['name']}\n"
                            f"ವಿಭಾಗ: {chapter.name}\n"
                            "ನಿಯಮಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ, "
                            "ಉದಾಹರಣೆಗಳನ್ನು ಗಮನಿಸಿ ಮತ್ತು "
                            "ಪರೀಕ್ಷಾ ಮಾದರಿಯ ಪ್ರಶ್ನೆಗಳನ್ನು "
                            "ಅಭ್ಯಾಸ ಮಾಡಿ."
                        ),

                        "easy_method": (
                            "ಹಂತ 1: ಮೂಲ ನಿಯಮ ಅಥವಾ ವಿಧಾನವನ್ನು "
                            "ತಿಳಿದುಕೊಳ್ಳಿ.\n"
                            "ಹಂತ 2: ಸರಳ ಉದಾಹರಣೆಗಳನ್ನು ನೋಡಿ.\n"
                            "ಹಂತ 3: ಸ್ವತಃ ಉದಾಹರಣೆಗಳನ್ನು "
                            "ಬರೆಯಿರಿ.\n"
                            "ಹಂತ 4: ಪರೀಕ್ಷಾ ಮಾದರಿಯ ಪ್ರಶ್ನೆಗಳನ್ನು "
                            "ಅಭ್ಯಾಸ ಮಾಡಿ.\n"
                            "ಹಂತ 5: ತಪ್ಪುಗಳನ್ನು ಪರಿಶೀಲಿಸಿ."
                        ),

                        "worked_example": (
                            f"ಅಭ್ಯಾಸ: '{item['name']}' "
                            "ವಿಷಯಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ಒಂದು ಸರಳ "
                            "ಉದಾಹರಣೆಯನ್ನು ಗುರುತಿಸಿ ಅಥವಾ "
                            "ರಚಿಸಿ ಮತ್ತು ಅದರ ನಿಯಮವನ್ನು "
                            "ವಿವರಿಸಿ."
                        ),

                        "common_mistakes": (
                            "1. ನಿಯಮವನ್ನು ಸರಿಯಾಗಿ ಓದದೆ "
                            "ಉತ್ತರಿಸುವುದು.\n"
                            "2. ಕಾಗುಣಿತದ ತಪ್ಪುಗಳನ್ನು "
                            "ನಿರ್ಲಕ್ಷಿಸುವುದು.\n"
                            "3. ಸಂದರ್ಭಕ್ಕೆ ಸರಿಯಾಗದ ಪದ ಅಥವಾ "
                            "ರೂಪವನ್ನು ಬಳಸುವುದು.\n"
                            "4. ಉತ್ತರದ ವಿನ್ಯಾಸವನ್ನು "
                            "ಗಮನಿಸದಿರುವುದು."
                        ),
                    },
                )

                topic_state = (
                    "CREATED"
                    if created
                    else "UPDATED"
                )

                self.stdout.write(
                    f"  [{topic_state}] "
                    f"{topic.name}"
                )

                total_topics += 1
                total_content += 1

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Kannada language skills "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Skill sections: "
            f"{len(KANNADA_FIRST_LANGUAGE_SKILLS)}"
        )

        self.stdout.write(
            f"Skill topics: {total_topics}"
        )

        self.stdout.write(
            f"Learning contents: {total_content}"
        )