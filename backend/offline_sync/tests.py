import uuid

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from courses.models import (
    AcademicYear,
    Board,
    Chapter,
    Grade,
    Subject,
    Topic,
)
from offline_sync.models import OfflineSyncRecord
from progress.models import QuizAttempt
from quizzes.models import Question, Quiz
from users.models import Student, Teacher


class OfflineSyncTests(APITestCase):

    def setUp(self):
        # -----------------------------------------------------
        # CURRICULUM
        # -----------------------------------------------------

        self.board = Board.objects.create(
            code="KSEAB",
            name="Karnataka School Examination "
                 "and Assessment Board",
            state="Karnataka",
            country="India",
            is_active=True,
        )

        self.academic_year = (
            AcademicYear.objects.create(
                board=self.board,
                name="2026-27",
                is_active=True,
            )
        )

        self.grade = Grade.objects.create(
            academic_year=self.academic_year,
            name="SSLC Class 10",
            level=10,
            description="Class 10",
        )

        self.subject = Subject.objects.create(
            grade=self.grade,
            name="Mathematics",
            description="Mathematics",
            language="English",
        )

        self.chapter = Chapter.objects.create(
            subject=self.subject,
            name="Real Numbers",
            chapter_number=1,
            description="Real Numbers chapter",
        )

        self.topic = Topic.objects.create(
            chapter=self.chapter,
            name="Introduction to Real Numbers",
            description="Introduction",
            difficulty=1,
        )

        # -----------------------------------------------------
        # QUIZ
        # -----------------------------------------------------

        self.quiz = Quiz.objects.create(
            topic=self.topic,
            title="Real Numbers Quiz",
            description="Test quiz",
        )

        self.questions = [
            Question.objects.create(
                quiz=self.quiz,
                question_text="Question 1",
                option_a="A1",
                option_b="B1",
                option_c="C1",
                option_d="D1",
                correct_answer="A",
                difficulty=1,
            ),
            Question.objects.create(
                quiz=self.quiz,
                question_text="Question 2",
                option_a="A2",
                option_b="B2",
                option_c="C2",
                option_d="D2",
                correct_answer="B",
                difficulty=1,
            ),
            Question.objects.create(
                quiz=self.quiz,
                question_text="Question 3",
                option_a="A3",
                option_b="B3",
                option_c="C3",
                option_d="D3",
                correct_answer="C",
                difficulty=1,
            ),
        ]

        # -----------------------------------------------------
        # STUDENT
        # -----------------------------------------------------

        self.student_user = User.objects.create_user(
            username="syncstudent",
            password="Student@123",
        )

        self.student = Student.objects.create(
            user=self.student_user,
            grade=self.grade,
            school="Demo High School",
            preferred_language="English",
        )

        self.student_token = Token.objects.create(
            user=self.student_user
        )

        # -----------------------------------------------------
        # TEACHER
        # -----------------------------------------------------

        self.teacher_user = User.objects.create_user(
            username="syncteacher",
            password="Teacher@123",
        )

        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            school="Demo High School",
        )

        self.teacher_token = Token.objects.create(
            user=self.teacher_user
        )

    def authenticate_student(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {self.student_token.key}"
            )
        )

    def authenticate_teacher(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {self.teacher_token.key}"
            )
        )

    def build_payload(
        self,
        client_attempt_id=None,
    ):
        if client_attempt_id is None:
            client_attempt_id = uuid.uuid4()

        return {
            "client_attempt_id": str(
                client_attempt_id
            ),
            "quiz_id": self.quiz.id,
            "device_id": "test-device",
            "answers": [
                {
                    "question": (
                        self.questions[0].id
                    ),
                    "answer": "A",
                },
                {
                    "question": (
                        self.questions[1].id
                    ),
                    "answer": "B",
                },
                {
                    "question": (
                        self.questions[2].id
                    ),
                    "answer": "C",
                },
            ],
        }

    # =========================================================
    # TEST 1
    # =========================================================

    def test_student_can_sync_offline_attempt(
        self
    ):
        self.authenticate_student()

        payload = self.build_payload()

        response = self.client.post(
            "/api/sync/quiz-attempts/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.data["status"],
            "synced",
        )

        self.assertFalse(
            response.data["already_synced"]
        )

        self.assertEqual(
            response.data["attempt"]["score"],
            3,
        )

        self.assertEqual(
            response.data["attempt"][
                "total_questions"
            ],
            3,
        )

        self.assertEqual(
            QuizAttempt.objects.count(),
            1,
        )

        self.assertEqual(
            OfflineSyncRecord.objects.count(),
            1,
        )

    # =========================================================
    # TEST 2
    # =========================================================

    def test_duplicate_sync_does_not_create_duplicate_attempt(
        self
    ):
        self.authenticate_student()

        attempt_uuid = uuid.uuid4()

        payload = self.build_payload(
            attempt_uuid
        )

        first_response = self.client.post(
            "/api/sync/quiz-attempts/",
            payload,
            format="json",
        )

        second_response = self.client.post(
            "/api/sync/quiz-attempts/",
            payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            201,
        )

        self.assertEqual(
            second_response.status_code,
            200,
        )

        self.assertTrue(
            second_response.data[
                "already_synced"
            ]
        )

        self.assertEqual(
            QuizAttempt.objects.count(),
            1,
        )

        self.assertEqual(
            OfflineSyncRecord.objects.count(),
            1,
        )

        self.assertEqual(
            first_response.data["attempt"][
                "attempt_id"
            ],
            second_response.data["attempt"][
                "attempt_id"
            ],
        )

    # =========================================================
    # TEST 3
    # =========================================================

    def test_invalid_uuid_is_rejected(
        self
    ):
        self.authenticate_student()

        payload = self.build_payload()

        payload[
            "client_attempt_id"
        ] = "invalid-uuid"

        response = self.client.post(
            "/api/sync/quiz-attempts/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            OfflineSyncRecord.objects.count(),
            0,
        )

        self.assertEqual(
            QuizAttempt.objects.count(),
            0,
        )

    # =========================================================
    # TEST 4
    # =========================================================

    def test_missing_quiz_creates_failed_sync_record(
        self
    ):
        self.authenticate_student()

        payload = self.build_payload()

        payload["quiz_id"] = 999999

        response = self.client.post(
            "/api/sync/quiz-attempts/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            OfflineSyncRecord.objects.count(),
            1,
        )

        record = (
            OfflineSyncRecord.objects.first()
        )

        self.assertEqual(
            record.status,
            "failed",
        )

        self.assertEqual(
            record.error_message,
            "Quiz not found.",
        )

        self.assertEqual(
            QuizAttempt.objects.count(),
            0,
        )

    # =========================================================
    # TEST 5
    # =========================================================

    def test_teacher_cannot_sync_student_attempt(
        self
    ):
        self.authenticate_teacher()

        payload = self.build_payload()

        response = self.client.post(
            "/api/sync/quiz-attempts/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            OfflineSyncRecord.objects.count(),
            0,
        )

        self.assertEqual(
            QuizAttempt.objects.count(),
            0,
        )

    # =========================================================
    # TEST 6
    # =========================================================

    def test_sync_status_returns_student_records(
        self
    ):
        self.authenticate_student()

        payload = self.build_payload()

        self.client.post(
            "/api/sync/quiz-attempts/",
            payload,
            format="json",
        )

        response = self.client.get(
            "/api/sync/status/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["summary"]["total"],
            1,
        )

        self.assertEqual(
            response.data["summary"]["synced"],
            1,
        )

        self.assertEqual(
            response.data["summary"]["pending"],
            0,
        )

        self.assertEqual(
            response.data["summary"]["failed"],
            0,
        )