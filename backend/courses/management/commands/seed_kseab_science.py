from django.core.management.base import BaseCommand
from django.db import transaction

from courses.data.kseab_science import SCIENCE_DATA
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
        "Bulk seed KSEAB SSLC Class 10 Science "
        "topics and learning content."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Bulk seeding KSEAB Science..."
            )
        )

        try:
            board = Board.objects.get(code="KSEAB")

            academic_year = AcademicYear.objects.get(
                board=board,
                name="2026-27",
            )

            grade = Grade.objects.get(
                academic_year=academic_year,
                name="SSLC Class 10",
            )

            science = Subject.objects.get(
                grade=grade,
                name="Science",
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
                    "KSEAB Science curriculum not found. "
                    "Run seed_kseab first."
                )
            )
            return

        total_topics = 0
        total_content = 0

        for chapter_number, data in SCIENCE_DATA.items():

            try:
                chapter = Chapter.objects.get(
                    subject=science,
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

            for item in data["topics"]:

                topic, created = Topic.objects.update_or_create(
                    chapter=chapter,
                    name=item["name"],
                    defaults={
                        "description": item["explanation"],
                        "difficulty": item["difficulty"],
                    },
                )

                LearningContent.objects.update_or_create(
                    topic=topic,
                    defaults={
                        "explanation": item["explanation"],
                        "key_concepts": item["key_concepts"],
                        "easy_method": (
                            "Step 1: Identify the scientific "
                            "idea involved.\n"
                            "Step 2: Recall the definition, "
                            "law or process.\n"
                            "Step 3: Connect it to the given "
                            "example.\n"
                            "Step 4: Apply the concept.\n"
                            "Step 5: Check the conclusion."
                        ),
                        "worked_example": item["worked_example"],
                        "common_mistakes": (
                            "1. Confusing similar scientific "
                            "terms.\n"
                            "2. Ignoring units or conditions.\n"
                            "3. Memorising without understanding "
                            "the process.\n"
                            "4. Applying a rule outside its "
                            "valid context."
                        ),
                    },
                )

                status = (
                    "CREATED"
                    if created
                    else "UPDATED"
                )

                self.stdout.write(
                    f"  [{status}] {topic.name}"
                )

                total_topics += 1
                total_content += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "KSEAB Science bulk curriculum "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Processed topics: {total_topics}"
        )

        self.stdout.write(
            f"Processed learning contents: "
            f"{total_content}"
        )