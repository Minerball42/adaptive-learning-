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
        "KSEAB SSLC First Language Kannada."
    )

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Bulk seeding First Language Kannada questions..."
            )
        )

        # =========================================================
        # LOCATE FIRST LANGUAGE KANNADA
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
                    "curriculum was not found."
                )
            )
            return

        # =========================================================
        # GET ALL 31 TOPICS
        # =========================================================

        topics = list(
            Topic.objects.filter(
                chapter__subject=kannada,
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
                    "No First Language Kannada "
                    "topics were found."
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
                    "Some Kannada topics have no "
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
        # PROCESS EVERY KANNADA TOPIC
        # =========================================================

        for topic in topics:

            content = learning_map[
                topic.id
            ]

                        # Prefer distractors from the same section.
            # If the section is small, use topics from the
            # same broad curriculum group before other topics.

            chapter_number = (
                topic.chapter.chapter_number
            )

            if chapter_number <= 3:
                broad_group = [
                    item
                    for item in topics
                    if (
                        item.id != topic.id
                        and item.chapter.chapter_number <= 3
                    )
                ]
            else:
                broad_group = [
                    item
                    for item in topics
                    if (
                        item.id != topic.id
                        and item.chapter.chapter_number >= 4
                    )
                ]

            same_section = [
                item
                for item in broad_group
                if (
                    item.chapter_id
                    == topic.chapter_id
                )
            ]

            same_group_other_section = [
                item
                for item in broad_group
                if (
                    item.chapter_id
                    != topic.chapter_id
                )
            ]

            remaining = [
                item
                for item in topics
                if (
                    item.id != topic.id
                    and item
                    not in broad_group
                )
            ]

            peers = (
                same_section
                + same_group_other_section
                + remaining
            )
            quiz, _ = Quiz.objects.update_or_create(
                topic=topic,
                title=f"{topic.name} Quiz",
                defaults={
                    "description": (
                        "KSEAB SSLC First Language Kannada "
                        "adaptive concept-check assessment "
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
                f"Section "
                f"{topic.chapter.chapter_number} | "
                f"{topic.name} | "
                f"created={topic_created} "
                f"updated={topic_updated} | "
                f"E/M/H={easy}/{medium}/{hard}"
            )

        # =========================================================
        # FINAL SUMMARY
        # =========================================================

        total_quizzes = Quiz.objects.filter(
            topic__chapter__subject=kannada
        ).count()

        total_questions = Question.objects.filter(
            quiz__topic__chapter__subject=kannada
        ).count()

        easy_total = Question.objects.filter(
            quiz__topic__chapter__subject=kannada,
            difficulty=1,
        ).count()

        medium_total = Question.objects.filter(
            quiz__topic__chapter__subject=kannada,
            difficulty=2,
        ).count()

        hard_total = Question.objects.filter(
            quiz__topic__chapter__subject=kannada,
            difficulty=3,
        ).count()

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "First Language Kannada question "
                "seed completed successfully."
            )
        )

        self.stdout.write(
            f"Topics processed: {len(topics)}"
        )

        self.stdout.write(
            f"Quizzes: {total_quizzes}"
        )

        self.stdout.write(
            f"Questions created: {total_created}"
        )

        self.stdout.write(
            f"Questions updated: {total_updated}"
        )

        self.stdout.write(
            f"Total questions: {total_questions}"
        )

        self.stdout.write(
            f"Easy: {easy_total}"
        )

        self.stdout.write(
            f"Medium: {medium_total}"
        )

        self.stdout.write(
            f"Hard: {hard_total}"
        )

    # =============================================================
    # BUILD 9 QUESTIONS PER TOPIC
    # =============================================================

    def _build_questions(
        self,
        topic,
        content,
        peers,
        learning_map,
    ):

        topic_name = topic.name

        section_name = (
            topic.chapter.name
        )

        explanation = self._snippet(
            content.explanation,
            fallback=(
                f"{topic_name} ವಿಷಯದ ಮುಖ್ಯ ವಿವರಣೆ"
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
                f"{topic_name} ವಿಷಯದ ಅಭ್ಯಾಸ"
            ),
        )

        peer_names = self._peer_values(
            peers,
            lambda peer: peer.name,
            exclude=topic_name,
        )

        peer_key_1 = self._peer_values(
            peers,
            lambda peer: (
                self._first_key_line(
                    learning_map[
                        peer.id
                    ]
                )
            ),
            exclude=key_1,
        )

        peer_key_2 = self._peer_values(
            peers,
            lambda peer: (
                self._second_key_line(
                    learning_map[
                        peer.id
                    ]
                )
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
                    f"{peer.name} ವಿಷಯದ ಅಭ್ಯಾಸ"
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
                    "ಈ ಕೆಳಗಿನ ವಿವರಣೆಗೆ ಅತ್ಯಂತ "
                    "ಸಂಬಂಧಿಸಿದ ವಿಷಯ ಯಾವುದು? "
                    f"'{explanation}'"
                ),
                correct=topic_name,
                distractors=peer_names,
                difficulty=1,
                position_seed=(
                    topic.id + 1
                ),
            )
        )

        # =========================================================
        # EASY 2
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    f"'{topic_name}' ವಿಷಯಕ್ಕೆ "
                    "ಸಂಬಂಧಿಸಿದ ಮುಖ್ಯ ಅಂಶ ಯಾವುದು?"
                ),
                correct=key_1,
                distractors=peer_key_1,
                difficulty=1,
                position_seed=(
                    topic.id + 2
                ),
            )
        )

        # =========================================================
        # EASY 3
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    f"'{topic_name}' ವಿಷಯಕ್ಕೆ "
                    "ಸಂಬಂಧಿಸಿದ ಅಭ್ಯಾಸ ಯಾವುದು?"
                ),
                correct=example,
                distractors=peer_examples,
                difficulty=1,
                position_seed=(
                    topic.id + 3
                ),
            )
        )

        # =========================================================
        # MEDIUM 1
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    f"'{key_1}' ಎಂಬ ಅಂಶವು "
                    "ಯಾವ ವಿಷಯಕ್ಕೆ ಹೆಚ್ಚು "
                    "ಸಂಬಂಧಿಸಿದೆ?"
                ),
                correct=topic_name,
                distractors=peer_names,
                difficulty=2,
                position_seed=(
                    topic.id + 4
                ),
            )
        )

        # =========================================================
        # MEDIUM 2
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    f"'{topic_name}' ವಿಷಯಕ್ಕೆ "
                    "ಸಂಬಂಧಿಸಿದ ಮತ್ತೊಂದು ಸರಿಯಾದ "
                    "ಅಂಶ ಯಾವುದು?"
                ),
                correct=key_2,
                distractors=peer_key_2,
                difficulty=2,
                position_seed=(
                    topic.id + 5
                ),
            )
        )

        # =========================================================
        # MEDIUM 3
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    "ವಿದ್ಯಾರ್ಥಿಯೊಬ್ಬರು ಈ ಅಭ್ಯಾಸವನ್ನು "
                    "ಮಾಡುತ್ತಿದ್ದಾರೆ: "
                    f"'{example}' "
                    "ಅವರು ಯಾವ ವಿಷಯವನ್ನು "
                    "ಪುನರವಲೋಕಿಸಬೇಕು?"
                ),
                correct=topic_name,
                distractors=peer_names,
                difficulty=2,
                position_seed=(
                    topic.id + 6
                ),
            )
        )

        # =========================================================
        # HARD 1
        # =========================================================

        correct_pair = self._snippet(
            (
                f"{topic_name} — "
                f"{key_1}"
            ),
            max_length=220,
        )

        peer_pairs = self._peer_values(
            peers,
            lambda peer: self._snippet(
                (
                    f"{peer.name} — "
                    f"{self._first_key_line(
                        learning_map[
                            peer.id
                        ]
                    )}"
                ),
                max_length=220,
            ),
            exclude=correct_pair,
        )

        questions.append(
            self._mcq(
                question_text=(
                    "ಯಾವ ಆಯ್ಕೆಯು ವಿಷಯ ಮತ್ತು ಅದರ "
                    "ಮುಖ್ಯ ಅಂಶವನ್ನು ಸರಿಯಾಗಿ "
                    "ಹೊಂದಿಸುತ್ತದೆ? "
                    f"ವಿಷಯ: '{topic_name}'"
                ),
                correct=correct_pair,
                distractors=peer_pairs,
                difficulty=3,
                position_seed=(
                    topic.id + 7
                ),
            )
        )

        # =========================================================
        # HARD 2
        # =========================================================

        questions.append(
            self._mcq(
                question_text=(
                    "ಈ ಎರಡೂ ಸುಳಿವುಗಳಿಗೆ ಅತ್ಯಂತ "
                    "ಸಂಬಂಧಿಸಿದ ವಿಷಯ ಯಾವುದು? "
                    f"ಮುಖ್ಯ ಅಂಶ: '{key_1}'. "
                    f"ಅಭ್ಯಾಸ: '{example}'."
                ),
                correct=topic_name,
                distractors=peer_names,
                difficulty=3,
                position_seed=(
                    topic.id + 8
                ),
            )
        )

        # =========================================================
        # HARD 3
        # =========================================================

        unrelated = (
            peer_key_1[0]
            if peer_key_1
            else "ಸಂಬಂಧಿಸದ ಭಾಷಾ ಅಂಶ"
        )

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
                f"{topic_name} ವಿಷಯದ "
                f"ಮುಖ್ಯ ಅಂಶ {fallback_number}"
            )

            if fallback not in associated:
                associated.append(
                    fallback
                )

            fallback_number += 1

        questions.append(
            self._mcq(
                question_text=(
                    "ಕೆಳಗಿನವುಗಳಲ್ಲಿ ಯಾವುದು "
                    f"'{topic_name}' ವಿಷಯಕ್ಕೆ "
                    "ಸಂಬಂಧಿಸಿಲ್ಲ?"
                ),
                correct=unrelated,
                distractors=associated[:3],
                difficulty=3,
                position_seed=(
                    topic.id + 9
                ),
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
                f"{topic.name}: expected "
                f"9 questions, "
                f"got {len(questions)}."
            )

        seen = set()

        counts = {
            1: 0,
            2: 0,
            3: 0,
        }

        for item in questions:

            text = (
                item["question_text"]
            )

            if text in seen:

                raise ValueError(
                    f"{topic.name}: duplicate "
                    "question text."
                )

            seen.add(
                text
            )

            difficulty = (
                item["difficulty"]
            )

            if difficulty not in counts:

                raise ValueError(
                    f"{topic.name}: invalid "
                    f"difficulty {difficulty}."
                )

            counts[
                difficulty
            ] += 1

            if item[
                "correct_answer"
            ] not in {
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

            if len(
                set(options)
            ) != 4:

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
                f"E/M/H=3/3/3, "
                f"got {counts}."
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

        while len(
            clean_distractors
        ) < 3:

            fallback = (
                "ಪರ್ಯಾಯ ಭಾಷಾ ಅಂಶ "
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

        position = (
            position_seed % 4
        )

        options = (
            clean_distractors[:3]
        )

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
            "question_text": (
                self._snippet(
                    question_text,
                    max_length=500,
                )
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
                values.append(
                    value
                )

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
                result.append(
                    value
                )

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
                "ಸಾಮಾನ್ಯ ಭಾಷಾ ಅಂಶ"
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
                "ಸಾಮಾನ್ಯ ಭಾಷಾ ಅಂಶ"
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