from django.core.management.base import BaseCommand
from django.db import transaction

from courses.data.kseab_social_science import (
    SOCIAL_SCIENCE_DATA,
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
        "Bulk seed KSEAB SSLC Class 10 Social Science "
        "topics and baseline learning content."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Bulk seeding KSEAB Social Science..."
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

            social_science = Subject.objects.get(
                grade=grade,
                name="Social Science",
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
                    "KSEAB Social Science curriculum "
                    "was not found. Run seed_kseab first."
                )
            )
            return

        total_topics = 0
        total_content = 0

        for chapter_number, data in (
            SOCIAL_SCIENCE_DATA.items()
        ):

            try:
                chapter = Chapter.objects.get(
                    subject=social_science,
                    chapter_number=chapter_number,
                    name=data["chapter"],
                )

            except Chapter.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Missing chapter {chapter_number}: "
                        f"{data['chapter']}"
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

            topic_names = data["topics"]
            topic_count = len(topic_names)

            for index, topic_name in enumerate(
                topic_names
            ):

                difficulty = self._difficulty(
                    index=index,
                    total=topic_count,
                )

                explanation = (
                    f"This topic studies {topic_name} "
                    f"within the KSEAB SSLC Social Science "
                    f"chapter '{chapter.name}'. It focuses "
                    "on the main facts, concepts, causes, "
                    "effects and relationships required "
                    "for understanding this part of the "
                    "chapter."
                )

                topic, created = (
                    Topic.objects.update_or_create(
                        chapter=chapter,
                        name=topic_name,
                        defaults={
                            "description": explanation,
                            "difficulty": difficulty,
                        },
                    )
                )

                LearningContent.objects.update_or_create(
                    topic=topic,
                    defaults={
                        "explanation": explanation,

                        "key_concepts": (
                            f"Chapter: {chapter.name}\n"
                            f"Main focus: {topic_name}\n"
                            "Understand important terms, "
                            "people, places, causes, effects "
                            "and relationships connected "
                            "with this topic."
                        ),

                        "easy_method": (
                            "Step 1: Read the topic heading.\n"
                            "Step 2: Identify important names, "
                            "dates, places and definitions.\n"
                            "Step 3: Separate causes, events "
                            "and effects where applicable.\n"
                            "Step 4: Connect the topic to the "
                            "main chapter theme.\n"
                            "Step 5: Revise using short notes, "
                            "maps, tables or timelines."
                        ),

                        "worked_example": (
                            f"Revision task: explain "
                            f"'{topic_name}' in the context "
                            f"of '{chapter.name}'. Identify "
                            "the main idea and at least two "
                            "supporting points from the "
                            "textbook."
                        ),

                        "common_mistakes": (
                            "1. Mixing events or concepts "
                            "from different chapters.\n"
                            "2. Memorising facts without "
                            "understanding cause and effect.\n"
                            "3. Confusing similar names, "
                            "dates or geographical terms.\n"
                            "4. Ignoring maps, timelines "
                            "and important definitions."
                        ),
                    },
                )

                state = (
                    "CREATED"
                    if created
                    else "UPDATED"
                )

                self.stdout.write(
                    f"  [{state}] {topic.name}"
                )

                total_topics += 1
                total_content += 1

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "KSEAB Social Science bulk curriculum "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Processed chapters: "
            f"{len(SOCIAL_SCIENCE_DATA)}"
        )

        self.stdout.write(
            f"Processed topics: {total_topics}"
        )

        self.stdout.write(
            f"Processed learning contents: "
            f"{total_content}"
        )

    def _difficulty(
        self,
        index,
        total,
    ):

        if index == 0:
            return 1

        if (
            total >= 4
            and index == total - 1
        ):
            return 3

        return 2