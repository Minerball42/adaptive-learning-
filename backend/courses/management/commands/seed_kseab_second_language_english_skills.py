from django.core.management.base import BaseCommand
from django.db import transaction

from courses.data.kseab_second_language_english_skills import (
    ENGLISH_SECOND_LANGUAGE_SKILLS,
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
        "Seed KSEAB SSLC Second Language English "
        "grammar, writing and comprehension skills."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding Second Language English skills..."
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
            ENGLISH_SECOND_LANGUAGE_SKILLS.items()
        ):

            chapter, chapter_created = (
                Chapter.objects.update_or_create(
                    subject=english,
                    chapter_number=chapter_number,
                    defaults={
                        "name": data["chapter"],
                        "description": (
                            "KSEAB SSLC Second Language "
                            f"English - {data['chapter']}"
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
                            f"Topic: {item['name']}\n"
                            f"Section: {chapter.name}\n"
                            "Understand the rule or skill, "
                            "study examples and practise "
                            "exam-style applications."
                        ),

                        "easy_method": (
                            "Step 1: Understand the basic rule "
                            "or format.\n"
                            "Step 2: Study simple examples.\n"
                            "Step 3: Identify how the rule is "
                            "used in context.\n"
                            "Step 4: Practise similar questions.\n"
                            "Step 5: Check and correct mistakes."
                        ),

                        "worked_example": (
                            f"Practice: Apply the rules or method "
                            f"of '{item['name']}' to a suitable "
                            "example and explain the answer."
                        ),

                        "common_mistakes": (
                            "1. Applying a rule without checking "
                            "the sentence context.\n"
                            "2. Ignoring spelling, punctuation "
                            "or grammar.\n"
                            "3. Using an incorrect format in "
                            "writing tasks.\n"
                            "4. Answering without reviewing the "
                            "completed response."
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
                "Second Language English skills "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Skill sections: "
            f"{len(ENGLISH_SECOND_LANGUAGE_SKILLS)}"
        )

        self.stdout.write(
            f"Skill topics: {total_topics}"
        )

        self.stdout.write(
            f"Learning contents: {total_content}"
        )