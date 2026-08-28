from django.core.management.base import BaseCommand
from django.db import transaction

from courses.data.kseab_third_language_hindi import (
    HINDI_THIRD_LANGUAGE_DATA,
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
        "Bulk seed KSEAB SSLC Third Language Hindi "
        "literature curriculum and learning content."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Bulk seeding Third Language Hindi..."
            )
        )

        # =========================================================
        # LOCATE THIRD LANGUAGE HINDI
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

            hindi = Subject.objects.get(
                grade=grade,
                name="Hindi",
                language="Hindi",
                subject_type="third_language",
            )

        except (
            Board.DoesNotExist,
            AcademicYear.DoesNotExist,
            Grade.DoesNotExist,
            Subject.DoesNotExist,
        ):
            self.stdout.write(
                self.style.ERROR(
                    "KSEAB Third Language Hindi "
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
            HINDI_THIRD_LANGUAGE_DATA.items()
        ):

            chapter, chapter_created = (
                Chapter.objects.update_or_create(
                    subject=hindi,
                    chapter_number=chapter_number,
                    defaults={
                        "name": data["chapter"],
                        "description": (
                            "KSEAB SSLC Third Language Hindi - "
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
                                "KSEAB SSLC Third Language "
                                f"Hindi lesson: {topic_name}"
                            ),
                            "difficulty": difficulty,
                        },
                    )
                )

                LearningContent.objects.update_or_create(
                    topic=topic,
                    defaults={
                        "explanation": (
                            f"'{topic_name}' पाठ को ध्यान से पढ़कर "
                            "उसके मुख्य विचार, घटनाएँ, पात्र, "
                            "संदेश और भाषा को समझें।"
                        ),

                        "key_concepts": (
                            f"पाठ: {topic_name}\n"
                            f"विभाग: {chapter.name}\n"
                            "मुख्य विचार, महत्वपूर्ण घटनाएँ, "
                            "पात्र, संदेश, शब्दार्थ तथा "
                            "पाठ-आधारित प्रश्न।"
                        ),

                        "easy_method": (
                            "चरण 1: पाठ को ध्यान से पढ़ें।\n"
                            "चरण 2: कठिन शब्दों के अर्थ समझें।\n"
                            "चरण 3: मुख्य विचार पहचानें।\n"
                            "चरण 4: महत्वपूर्ण घटनाओं और "
                            "पात्रों को नोट करें।\n"
                            "चरण 5: पाठ-आधारित प्रश्नों का "
                            "अभ्यास करें।"
                        ),

                        "worked_example": (
                            f"अभ्यास: '{topic_name}' पाठ का "
                            "मुख्य विचार लिखिए और पाठ से "
                            "दो महत्वपूर्ण बिंदु बताइए।"
                        ),

                        "common_mistakes": (
                            "1. पाठ का अर्थ समझे बिना केवल "
                            "उत्तर याद करना।\n"
                            "2. प्रश्न से असंबंधित उत्तर लिखना।\n"
                            "3. शब्दार्थ और संदर्भ पर ध्यान "
                            "न देना।\n"
                            "4. वर्तनी और व्याकरण की गलतियों "
                            "को न सुधारना।"
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
                "Third Language Hindi literature "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Sections: "
            f"{len(HINDI_THIRD_LANGUAGE_DATA)}"
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