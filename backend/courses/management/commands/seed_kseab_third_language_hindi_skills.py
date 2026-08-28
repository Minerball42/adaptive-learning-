from django.core.management.base import BaseCommand
from django.db import transaction

from courses.data.kseab_third_language_hindi_skills import (
    HINDI_THIRD_LANGUAGE_SKILLS,
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
        "Seed KSEAB SSLC Third Language Hindi "
        "grammar, writing and comprehension skills."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding Third Language Hindi skills..."
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
                    "subject was not found."
                )
            )
            return

        total_topics = 0
        total_content = 0

        # =========================================================
        # CREATE SKILL SECTIONS
        # =========================================================

        for chapter_number, data in (
            HINDI_THIRD_LANGUAGE_SKILLS.items()
        ):

            chapter, chapter_created = (
                Chapter.objects.update_or_create(
                    subject=hindi,
                    chapter_number=chapter_number,
                    defaults={
                        "name": data["chapter"],
                        "description": (
                            "KSEAB SSLC Third Language "
                            f"Hindi - {data['chapter']}"
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

            # =====================================================
            # CREATE TOPICS
            # =====================================================

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
                            f"विषय: {item['name']}\n"
                            f"विभाग: {chapter.name}\n"
                            "नियम या कौशल को समझें, "
                            "उदाहरणों का अध्ययन करें तथा "
                            "परीक्षा-आधारित प्रश्नों का "
                            "अभ्यास करें।"
                        ),

                        "easy_method": (
                            "चरण 1: मूल नियम या प्रारूप "
                            "समझें।\n"
                            "चरण 2: सरल उदाहरण देखें।\n"
                            "चरण 3: नियम का प्रयोग पहचानें।\n"
                            "चरण 4: समान प्रश्नों का अभ्यास "
                            "करें।\n"
                            "चरण 5: उत्तर की जाँच करके "
                            "गलतियाँ सुधारें।"
                        ),

                        "worked_example": (
                            f"अभ्यास: '{item['name']}' "
                            "से संबंधित एक उपयुक्त उदाहरण "
                            "पर नियम या विधि लागू कीजिए "
                            "और उत्तर समझाइए।"
                        ),

                        "common_mistakes": (
                            "1. नियम को समझे बिना उत्तर देना।\n"
                            "2. वर्तनी और व्याकरण की "
                            "गलतियों को न सुधारना।\n"
                            "3. प्रसंग के अनुसार सही शब्द "
                            "या रूप का प्रयोग न करना।\n"
                            "4. लेखन कार्य में उचित प्रारूप "
                            "का पालन न करना।"
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

        # =========================================================
        # SUMMARY
        # =========================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Third Language Hindi skills "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Skill sections: "
            f"{len(HINDI_THIRD_LANGUAGE_SKILLS)}"
        )

        self.stdout.write(
            f"Skill topics: {total_topics}"
        )

        self.stdout.write(
            f"Learning contents: {total_content}"
        )