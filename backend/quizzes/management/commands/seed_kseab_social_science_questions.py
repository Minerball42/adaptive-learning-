from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import (
    Board,
    AcademicYear,
    Grade,
    Subject,
    Topic,
    LearningContent,
)

from quizzes.models import (
    Quiz,
    Question,
)


class Command(BaseCommand):
    help = (
        "Bulk seed baseline adaptive questions for "
        "KSEAB SSLC Class 10 Social Science."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Bulk seeding KSEAB Social Science questions..."
            )
        )

        # =========================================================
        # LOCATE SCIENCE
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

            science = Subject.objects.get(
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
                    "KSEAB Social Science curriculum was not found. "
                    "Run seed_kseab and seed_kseab_science "
                    "first."
                )
            )
            return

        topics = list(
            Topic.objects.filter(
                chapter__subject=science,
            )
            .select_related("chapter")
            .order_by(
                "chapter__chapter_number",
                "id",
            )
        )

        if not topics:
            self.stdout.write(
                self.style.ERROR(
                    "No Social Science topics found. "
                    "Run seed_kseab_science first."
                )
            )
            return

        # =========================================================
        # LEARNING CONTENT MAP
        # =========================================================

        learning_map = {
            content.topic_id: content
            for content in (
                LearningContent.objects.filter(
                    topic__in=topics
                )
                .select_related("topic")
            )
        }

        missing = [
            topic.name
            for topic in topics
            if topic.id not in learning_map
        ]

        if missing:
            self.stdout.write(
                self.style.ERROR(
                    "Some Social Science topics have no "
                    "LearningContent:"
                )
            )

            for name in missing:
                self.stdout.write(
                    f"  - {name}"
                )

            return

        total_created = 0
        total_updated = 0

        # =========================================================
        # PROCESS ALL SCIENCE TOPICS
        # =========================================================

        for topic in topics:

            content = learning_map[topic.id]

            peers = [
                item
                for item in topics
                if item.id != topic.id
            ]

            quiz, _ = Quiz.objects.update_or_create(
                topic=topic,
                title=f"{topic.name} Quiz",
                defaults={
                    "description": (
                        "Adaptive concept-check assessment "
                        f"for {topic.name}."
                    )
                },
            )

            questions = self._build_questions(
                topic=topic,
                content=content,
                peers=peers,
                learning_map=learning_map,
            )

            self._validate_questions(
                topic=topic,
                questions=questions,
            )

            topic_created = 0
            topic_updated = 0

            for data in questions:

                _, created = (
                    Question.objects.update_or_create(
                        quiz=quiz,
                        question_text=(
                            data["question_text"]
                        ),
                        defaults={
                            "option_a": (
                                data["option_a"]
                            ),
                            "option_b": (
                                data["option_b"]
                            ),
                            "option_c": (
                                data["option_c"]
                            ),
                            "option_d": (
                                data["option_d"]
                            ),
                            "correct_answer": (
                                data["correct_answer"]
                            ),
                            "difficulty": (
                                data["difficulty"]
                            ),
                        },
                    )
                )

                if created:
                    topic_created += 1
                    total_created += 1
                else:
                    topic_updated += 1
                    total_updated += 1

            easy = quiz.questions.filter(
                difficulty=1
            ).count()

            medium = quiz.questions.filter(
                difficulty=2
            ).count()

            hard = quiz.questions.filter(
                difficulty=3
            ).count()

            self.stdout.write(
                f"Chapter "
                f"{topic.chapter.chapter_number} | "
                f"{topic.name} | "
                f"created={topic_created} "
                f"updated={topic_updated} | "
                f"E/M/H={easy}/{medium}/{hard}"
            )

        # =========================================================
        # SUMMARY
        # =========================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "KSEAB Social Science bulk question "
                "seed completed."
            )
        )

        self.stdout.write(
            f"Topics processed: {len(topics)}"
        )

        self.stdout.write(
            f"Questions created: {total_created}"
        )

        self.stdout.write(
            f"Questions updated: {total_updated}"
        )

    # =============================================================
    # BUILD 9 QUESTIONS FOR EACH TOPIC
    # =============================================================

    def _build_questions(
        self,
        topic,
        content,
        peers,
        learning_map,
    ):

        topic_name = topic.name

        explanation = self._snippet(
            content.explanation,
            fallback=(
                f"Core social science concept from "
                f"{topic_name}"
            ),
        )

        key_lines = self._lines(
            content.key_concepts
        )

        key_1 = (
            key_lines[0]
            if key_lines
            else explanation
        )

        key_2 = (
            key_lines[1]
            if len(key_lines) > 1
            else explanation
        )

        example = self._snippet(
            content.worked_example,
            fallback=(
                f"Worked example for {topic_name}"
            ),
        )

        peer_names = self._peer_values(
            peers,
            lambda peer: peer.name,
            exclude=topic_name,
        )

        peer_key_1 = self._peer_values(
            peers,
            lambda peer: self._first_key_line(
                learning_map[peer.id]
            ),
            exclude=key_1,
        )

        peer_key_2 = self._peer_values(
            peers,
            lambda peer: self._second_key_line(
                learning_map[peer.id]
            ),
            exclude=key_2,
        )

        peer_examples = self._peer_values(
            peers,
            lambda peer: self._snippet(
                learning_map[
                    peer.id
                ].worked_example,
                fallback=(
                    f"Worked example for "
                    f"{peer.name}"
                ),
            ),
            exclude=example,
        )

        questions = []

        # =========================================================
        # EASY 1
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    "Which Social Science topic is best "
                    "described by: "
                    f"'{explanation}'?"
                ),
                correct=topic_name,
                distractors=peer_names,
                difficulty=1,
                position_seed=topic.id + 1,
            )
        )

        # =========================================================
        # EASY 2
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    "Which key concept belongs to "
                    f"'{topic_name}'?"
                ),
                correct=key_1,
                distractors=peer_key_1,
                difficulty=1,
                position_seed=topic.id + 2,
            )
        )

        # =========================================================
        # EASY 3
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    "Which example is associated "
                    f"with '{topic_name}'?"
                ),
                correct=example,
                distractors=peer_examples,
                difficulty=1,
                position_seed=topic.id + 3,
            )
        )

        # =========================================================
        # MEDIUM 1
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    f"The concept '{key_1}' is most "
                    "directly associated with which "
                    "Social Science topic?"
                ),
                correct=topic_name,
                distractors=peer_names,
                difficulty=2,
                position_seed=topic.id + 4,
            )
        )

        # =========================================================
        # MEDIUM 2
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    "Which statement is also associated "
                    f"with '{topic_name}'?"
                ),
                correct=key_2,
                distractors=peer_key_2,
                difficulty=2,
                position_seed=topic.id + 5,
            )
        )

        # =========================================================
        # MEDIUM 3
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    "A student is studying this example: "
                    f"'{example}' "
                    "Which topic should they revise?"
                ),
                correct=topic_name,
                distractors=peer_names,
                difficulty=2,
                position_seed=topic.id + 6,
            )
        )

        # =========================================================
        # HARD 1
        # =========================================================

        correct_pair = self._snippet(
            f"{topic_name} â€” {key_1}",
            max_length=220,
        )

        peer_pairs = self._peer_values(
            peers,
            lambda peer: self._snippet(
                (
                    f"{peer.name} â€” "
                    f"{self._first_key_line(
                        learning_map[peer.id]
                    )}"
                ),
                max_length=220,
            ),
            exclude=correct_pair,
        )

        questions.append(
            self._mcq(
                question_text=(
                    "Which option correctly matches "
                    f"'{topic_name}' with one of "
                    "its key concepts?"
                ),
                correct=correct_pair,
                distractors=peer_pairs,
                difficulty=3,
                position_seed=topic.id + 7,
            )
        )

        # =========================================================
        # HARD 2
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    "Which Social Science topic is best matched "
                    "by BOTH clues? "
                    f"Concept: '{key_1}'. "
                    f"Example: '{example}'."
                ),
                correct=topic_name,
                distractors=peer_names,
                difficulty=3,
                position_seed=topic.id + 8,
            )
        )

        # =========================================================
        # HARD 3
        # =========================================================

        unrelated = peer_key_1[0]

        associated = self._unique_values(
            [
                key_1,
                key_2,
                explanation,
                example,
            ],
            exclude=unrelated,
        )

        fallback_number = 1

        while len(associated) < 3:

            fallback = (
                f"Core idea {fallback_number} "
                f"from {topic_name}"
            )

            if fallback not in associated:
                associated.append(
                    fallback
                )

            fallback_number += 1

        questions.append(
            self._mcq(
                question_text=(
                    "Which statement is NOT associated "
                    f"with '{topic_name}'?"
                ),
                correct=unrelated,
                distractors=associated[:3],
                difficulty=3,
                position_seed=topic.id + 9,
            )
        )

        return questions

    # =============================================================
    # VALIDATION
    # =============================================================

    def _validate_questions(
        self,
        topic,
        questions,
    ):

        if len(questions) != 9:
            raise ValueError(
                f"{topic.name}: expected 9 questions, "
                f"got {len(questions)}."
            )

        seen = set()

        counts = {
            1: 0,
            2: 0,
            3: 0,
        }

        for item in questions:

            text = item["question_text"]

            if text in seen:
                raise ValueError(
                    f"{topic.name}: duplicate "
                    "question text."
                )

            seen.add(text)

            difficulty = item["difficulty"]

            if difficulty not in counts:
                raise ValueError(
                    f"{topic.name}: invalid "
                    f"difficulty {difficulty}."
                )

            counts[difficulty] += 1

            if item["correct_answer"] not in {
                "A",
                "B",
                "C",
                "D",
            }:
                raise ValueError(
                    f"{topic.name}: invalid "
                    "correct answer."
                )

            options = [
                item["option_a"],
                item["option_b"],
                item["option_c"],
                item["option_d"],
            ]

            if len(set(options)) != 4:
                raise ValueError(
                    f"{topic.name}: duplicate "
                    "options detected."
                )

        expected = {
            1: 3,
            2: 3,
            3: 3,
        }

        if counts != expected:
            raise ValueError(
                f"{topic.name}: expected "
                f"E/M/H=3/3/3, got {counts}."
            )

    # =============================================================
    # MCQ BUILDER
    # =============================================================

    def _mcq(
        self,
        question_text,
        correct,
        distractors,
        difficulty,
        position_seed,
    ):

        correct = self._snippet(
            correct,
            max_length=220,
        )

        clean_distractors = (
            self._unique_values(
                distractors,
                exclude=correct,
            )
        )

        fallback_number = 1

        while len(clean_distractors) < 3:

            fallback = (
                "Alternative social science concept "
                f"{fallback_number}"
            )

            if (
                fallback != correct
                and fallback
                not in clean_distractors
            ):
                clean_distractors.append(
                    fallback
                )

            fallback_number += 1

        position = position_seed % 4

        options = clean_distractors[:3]

        options.insert(
            position,
            correct,
        )

        letters = [
            "A",
            "B",
            "C",
            "D",
        ]

        return {
            "question_text": self._snippet(
                question_text,
                max_length=500,
            ),
            "option_a": options[0],
            "option_b": options[1],
            "option_c": options[2],
            "option_d": options[3],
            "correct_answer": (
                letters[position]
            ),
            "difficulty": difficulty,
        }

    # =============================================================
    # HELPERS
    # =============================================================

    def _peer_values(
        self,
        peers,
        value_func,
        exclude,
    ):

        values = []

        for peer in peers:

            value = self._snippet(
                value_func(peer),
                max_length=220,
            )

            if (
                value
                and value != exclude
                and value not in values
            ):
                values.append(value)

            if len(values) >= 8:
                break

        return values

    def _unique_values(
        self,
        values,
        exclude=None,
    ):

        result = []

        for value in values:

            value = self._snippet(
                value,
                max_length=220,
            )

            if not value:
                continue

            if (
                exclude is not None
                and value == exclude
            ):
                continue

            if value not in result:
                result.append(value)

        return result

    def _first_key_line(
        self,
        content,
    ):

        lines = self._lines(
            content.key_concepts
        )

        if lines:
            return lines[0]

        return self._snippet(
            content.explanation,
            fallback=(
                "General social science concept"
            ),
        )

    def _second_key_line(
        self,
        content,
    ):

        lines = self._lines(
            content.key_concepts
        )

        if len(lines) > 1:
            return lines[1]

        if lines:
            return lines[0]

        return self._snippet(
            content.explanation,
            fallback=(
                "General social science concept"
            ),
        )

    def _lines(
        self,
        text,
    ):

        if not text:
            return []

        return [
            self._snippet(
                line,
                max_length=220,
            )
            for line in (
                str(text).splitlines()
            )
            if line.strip()
        ]

    def _snippet(
        self,
        text,
        fallback="",
        max_length=180,
    ):

        value = " ".join(
            str(
                text or fallback
            ).split()
        ).strip()

        if len(value) <= max_length:
            return value

        return (
            value[
                : max_length - 3
            ].rstrip()
            + "..."
        )
