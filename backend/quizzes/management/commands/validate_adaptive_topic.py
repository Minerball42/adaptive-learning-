import json

from django.contrib.auth import get_user_model
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from courses.models import Topic

from quizzes.models import (
    Question,
    AdaptiveQuizSession,
)


class Command(BaseCommand):
    help = (
        "Validate an adaptive topic through "
        "Easy -> Medium -> Hard and verify "
        "that the next topic unlocks."
    )

    # =============================================================
    # COMMAND ARGUMENTS
    # =============================================================

    def add_arguments(self, parser):

        parser.add_argument(
            "topic_id",
            type=int,
            help="Topic ID to validate.",
        )

        parser.add_argument(
            "--username",
            default="teststudent",
            help=(
                "Student username used for validation. "
                "Default: teststudent"
            ),
        )

    # =============================================================
    # RESPONSE HELPER
    # =============================================================

    def _response_data(self, response):

        if hasattr(response, "data"):
            return response.data

        try:
            text = response.content.decode(
                "utf-8",
                errors="replace",
            )

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

        except Exception:
            return (
                "Unable to read response body."
            )

    # =============================================================
    # CANCEL VALIDATION-ONLY SESSION
    # =============================================================

    def _cancel_session(self, session_id):

        if not session_id:
            return

        AdaptiveQuizSession.objects.filter(
            id=session_id,
            status="active",
        ).update(
            status="cancelled"
        )

    # =============================================================
    # MAIN COMMAND
    # =============================================================

    def handle(self, *args, **options):

        topic_id = options["topic_id"]
        username = options["username"]

        User = get_user_model()

        # =========================================================
        # LOCATE USER
        # =========================================================

        try:
            user = User.objects.get(
                username=username
            )

        except User.DoesNotExist:

            raise CommandError(
                f"User '{username}' does not exist."
            )

        # =========================================================
        # LOCATE TOKEN
        # =========================================================

        try:
            token = Token.objects.get(
                user=user
            )

        except Token.DoesNotExist:

            raise CommandError(
                f"No API token exists for "
                f"'{username}'."
            )

        # =========================================================
        # LOCATE TOPIC
        # =========================================================

        try:
            topic = (
                Topic.objects
                .select_related(
                    "chapter__subject"
                )
                .get(
                    id=topic_id
                )
            )

        except Topic.DoesNotExist:

            raise CommandError(
                f"Topic {topic_id} "
                "does not exist."
            )

        # =========================================================
        # API CLIENT
        # =========================================================

        client = APIClient()

        client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {token.key}"
            )
        )

        # Important:
        # APIClient normally uses "testserver".
        # Our project may reject that host.
        request_host = "127.0.0.1"

        # =========================================================
        # HEADER
        # =========================================================

        self.stdout.write("")

        self.stdout.write(
            "=" * 60
        )

        self.stdout.write(
            "ADAPTIVE VALIDATION"
        )

        self.stdout.write(
            "=" * 60
        )

        self.stdout.write(
            f"Student: {username}"
        )

        self.stdout.write(
            f"Topic: "
            f"{topic.id} | "
            f"{topic.name}"
        )

        self.stdout.write(
            f"Subject: "
            f"{topic.chapter.subject.name}"
        )

        final_mastery = None

        # =========================================================
        # ADAPTIVE LOOP
        #
        # It automatically continues:
        #
        # Easy -> Medium -> Hard -> Strong
        #
        # It also supports a partially completed topic.
        # =========================================================

        for round_number in range(
            1,
            5,
        ):

            # =====================================================
            # GET CURRENT ADAPTIVE QUIZ
            # =====================================================

            response = client.get(
                "/api/quizzes/adaptive/",
                {
                    "topic": topic_id,
                },
                HTTP_HOST=request_host,
            )

            response_data = (
                self._response_data(
                    response
                )
            )

            if response.status_code != 200:

                raise CommandError(
                    "Adaptive GET failed: "
                    f"{response.status_code} "
                    f"{response_data}"
                )

            session = response_data[
                "session"
            ]

            session_id = str(
                session["id"]
            )

            mastery_before = (
                response_data[
                    "mastery"
                ]
            )

            selection = (
                response_data[
                    "adaptive_selection"
                ]
            )

            difficulty = (
                selection[
                    "difficulty"
                ]
            )

            questions = (
                response_data[
                    "questions"
                ]
            )

            # =====================================================
            # TOPIC ALREADY STRONG
            # =====================================================

            if (
                mastery_before["level"]
                == "strong"
            ):

                final_mastery = (
                    mastery_before
                )

                # GET created a validation-only session.
                # We do not want to leave it active.
                self._cancel_session(
                    session_id
                )

                self.stdout.write("")

                self.stdout.write(
                    self.style.SUCCESS(
                        "Topic is already STRONG."
                    )
                )

                break

            # =====================================================
            # SHOW CURRENT ROUND
            # =====================================================

            self.stdout.write("")

            self.stdout.write(
                "-" * 60
            )

            self.stdout.write(
                f"ROUND {round_number}: "
                f"{difficulty.upper()}"
            )

            self.stdout.write(
                f"Session: {session_id}"
            )

            self.stdout.write(
                f"Questions returned: "
                f"{len(questions)}"
            )

            if not questions:

                self._cancel_session(
                    session_id
                )

                raise CommandError(
                    "Adaptive API returned "
                    "no questions."
                )

            # =====================================================
            # AUTOMATICALLY READ CORRECT ANSWERS
            # FROM LOCAL QUESTION BANK
            # =====================================================

            answers = []

            for item in questions:

                question_id = item[
                    "id"
                ]

                try:
                    question = (
                        Question.objects.get(
                            id=question_id
                        )
                    )

                except Question.DoesNotExist:

                    self._cancel_session(
                        session_id
                    )

                    raise CommandError(
                        "Question "
                        f"{question_id} "
                        "does not exist."
                    )

                correct_answer = (
                    question.correct_answer
                )

                answers.append(
                    {
                        "question": (
                            question.id
                        ),
                        "answer": (
                            correct_answer
                        ),
                    }
                )

                self.stdout.write(
                    f"Q{question.id} "
                    f"-> "
                    f"{correct_answer}"
                )

            # =====================================================
            # SUBMIT WHOLE SESSION
            # =====================================================

            submit_response = (
                client.post(
                    (
                        "/api/quizzes/"
                        "adaptive/submit/"
                    ),
                    {
                        "session_id": (
                            session_id
                        ),
                        "answers": answers,
                    },
                    format="json",
                    HTTP_HOST=request_host,
                )
            )

            submit_data = (
                self._response_data(
                    submit_response
                )
            )

            if not (
                200
                <= submit_response.status_code
                < 300
            ):

                self._cancel_session(
                    session_id
                )

                raise CommandError(
                    "Adaptive submit failed: "
                    f"{submit_response.status_code} "
                    f"{submit_data}"
                )

            # =====================================================
            # ATTEMPT RESULT
            # =====================================================

            attempt = submit_data[
                "attempt"
            ]

            final_mastery = (
                submit_data[
                    "mastery_after"
                ]
            )

            next_difficulty = (
                submit_data[
                    "next_adaptive_difficulty"
                ]
            )

            self.stdout.write(
                f"Score: "
                f"{attempt['score']}/"
                f"{attempt['total_questions']}"
            )

            self.stdout.write(
                f"Percentage: "
                f"{attempt['percentage']}%"
            )

            self.stdout.write(
                f"Mastery score: "
                f"{final_mastery['mastery_score']}"
            )

            self.stdout.write(
                f"Mastery level: "
                f"{final_mastery['level']}"
            )

            self.stdout.write(
                f"Next difficulty: "
                f"{next_difficulty['name']}"
            )

            # =====================================================
            # STOP ON STRONG
            # =====================================================

            if (
                final_mastery[
                    "level"
                ]
                == "strong"
            ):
                break

        # =========================================================
        # SAFETY CHECK
        # =========================================================

        if final_mastery is None:

            raise CommandError(
                "No mastery result "
                "was produced."
            )

        # =========================================================
        # FINAL MASTERY REPORT
        # =========================================================

        self.stdout.write("")

        self.stdout.write(
            "=" * 60
        )

        self.stdout.write(
            "FINAL MASTERY"
        )

        self.stdout.write(
            "=" * 60
        )

        self.stdout.write(
            f"Correct: "
            f"{final_mastery['correct']}/"
            f"{final_mastery['total']}"
        )

        self.stdout.write(
            f"Percentage: "
            f"{final_mastery['percentage']}"
        )

        self.stdout.write(
            f"Mastery score: "
            f"{final_mastery['mastery_score']}"
        )

        self.stdout.write(
            f"Level: "
            f"{final_mastery['level']}"
        )

        performance = (
            final_mastery[
                "difficulty_performance"
            ]
        )

        self.stdout.write("")

        self.stdout.write(
            "Difficulty performance:"
        )

        for name in [
            "easy",
            "medium",
            "hard",
        ]:

            stats = performance[
                name
            ]

            self.stdout.write(
                f"  {name.title()}: "
                f"{stats['correct']}/"
                f"{stats['total']} "
                f"({stats['percentage']}%)"
            )

        # =========================================================
        # VERIFY STRONG MASTERY
        # =========================================================

        if (
            final_mastery["level"]
            != "strong"
        ):

            raise CommandError(
                "Topic did not reach "
                "STRONG mastery."
            )

        # =========================================================
        # FIND NEXT TOPIC
        # =========================================================

        subject = (
            topic.chapter.subject
        )

        topics = list(
            Topic.objects.filter(
                chapter__subject=subject
            )
            .select_related(
                "chapter"
            )
            .order_by(
                "chapter__chapter_number",
                "id",
            )
        )

        try:
            current_index = next(
                index
                for index, item
                in enumerate(topics)
                if item.id == topic.id
            )

        except StopIteration:

            raise CommandError(
                "Could not locate topic "
                "inside subject ordering."
            )

        # =========================================================
        # NEXT TOPIC EXISTS
        # =========================================================

        if (
            current_index + 1
            < len(topics)
        ):

            next_topic = (
                topics[
                    current_index + 1
                ]
            )

            self.stdout.write("")

            self.stdout.write(
                "=" * 60
            )

            self.stdout.write(
                "NEXT TOPIC UNLOCK TEST"
            )

            self.stdout.write(
                "=" * 60
            )

            self.stdout.write(
                f"Next: "
                f"{next_topic.id} | "
                f"{next_topic.name}"
            )

            # =====================================================
            # REQUEST NEXT TOPIC
            # =====================================================

            next_response = (
                client.get(
                    "/api/quizzes/adaptive/",
                    {
                        "topic": (
                            next_topic.id
                        ),
                    },
                    HTTP_HOST=request_host,
                )
            )

            next_data = (
                self._response_data(
                    next_response
                )
            )

            if (
                next_response.status_code
                != 200
            ):

                raise CommandError(
                    "Next topic is still "
                    "locked or unavailable: "
                    f"{next_response.status_code} "
                    f"{next_data}"
                )

            self.stdout.write(
                self.style.SUCCESS(
                    "Status: UNLOCKED"
                )
            )

            next_selection = (
                next_data[
                    "adaptive_selection"
                ]
            )

            self.stdout.write(
                "Starting difficulty: "
                f"{next_selection['difficulty']}"
            )

            self.stdout.write(
                "Difficulty value: "
                f"{next_selection['difficulty_value']}"
            )

            # =====================================================
            # CANCEL THE NEXT-TOPIC SESSION
            #
            # We only opened it to check unlocking.
            # =====================================================

            next_session = (
                next_data
                .get(
                    "session",
                    {}
                )
                .get(
                    "id"
                )
            )

            if next_session:

                self._cancel_session(
                    str(next_session)
                )

        # =========================================================
        # LAST TOPIC
        # =========================================================

        else:

            self.stdout.write("")

            self.stdout.write(
                "This is the final topic "
                "in the subject."
            )

            self.stdout.write(
                "No next-topic unlock "
                "test is required."
            )

        # =========================================================
        # SUCCESS
        # =========================================================

        self.stdout.write("")

        self.stdout.write(
            "=" * 60
        )

        self.stdout.write(
            self.style.SUCCESS(
                "ADAPTIVE VALIDATION PASSED"
            )
        )

        self.stdout.write(
            "=" * 60
        )