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

from progress.models import QuizAttempt

from quizzes.models import (
    AdaptiveQuizSession,
    Question,
    Quiz,
)

from users.models import Student


class AdaptiveQuizTests(APITestCase):

    def setUp(self):

        # =====================================================
        # CURRICULUM
        # =====================================================

        self.board = Board.objects.create(
            code="KSEAB",
            name=(
                "Karnataka School Examination "
                "and Assessment Board"
            ),
            state="Karnataka",
            country="India",
            is_active=True,
        )

        self.academic_year = AcademicYear.objects.create(
            board=self.board,
            name="2026-27",
            is_active=True,
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
            name="Test Chapter",
            chapter_number=1,
            description="Adaptive test chapter",
        )

        # =====================================================
        # TOPICS
        # =====================================================

        self.topic1 = Topic.objects.create(
            chapter=self.chapter,
            name="Test Topic 1",
            description="First adaptive topic",
            difficulty=1,
        )

        self.topic2 = Topic.objects.create(
            chapter=self.chapter,
            name="Test Topic 2",
            description="Second adaptive topic",
            difficulty=1,
        )

        # =====================================================
        # QUIZ FOR TOPIC 1
        # =====================================================

        self.quiz = Quiz.objects.create(
            topic=self.topic1,
            title="Adaptive Test Quiz",
            description="Adaptive test quiz",
        )

        # =====================================================
        # EASY QUESTIONS
        # =====================================================

        self.easy_questions = [
            self.create_question(
                text="Easy Question 1",
                correct_answer="A",
                difficulty=1,
            ),
            self.create_question(
                text="Easy Question 2",
                correct_answer="B",
                difficulty=1,
            ),
            self.create_question(
                text="Easy Question 3",
                correct_answer="C",
                difficulty=1,
            ),
        ]

        # =====================================================
        # MEDIUM QUESTIONS
        # =====================================================

        self.medium_questions = [
            self.create_question(
                text="Medium Question 1",
                correct_answer="B",
                difficulty=2,
            ),
            self.create_question(
                text="Medium Question 2",
                correct_answer="C",
                difficulty=2,
            ),
            self.create_question(
                text="Medium Question 3",
                correct_answer="D",
                difficulty=2,
            ),
        ]

        # =====================================================
        # HARD QUESTIONS
        # =====================================================

        self.hard_questions = [
            self.create_question(
                text="Hard Question 1",
                correct_answer="C",
                difficulty=3,
            ),
            self.create_question(
                text="Hard Question 2",
                correct_answer="D",
                difficulty=3,
            ),
            self.create_question(
                text="Hard Question 3",
                correct_answer="A",
                difficulty=3,
            ),
        ]

        # =====================================================
        # STUDENT
        # =====================================================

        self.user = User.objects.create_user(
            username="adaptivestudent",
            password="Student@123",
        )

        self.student = Student.objects.create(
            user=self.user,
            grade=self.grade,
            school="Demo High School",
            preferred_language="English",
        )

        self.token = Token.objects.create(
            user=self.user
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {self.token.key}"
            )
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def create_question(
        self,
        text,
        correct_answer,
        difficulty,
    ):
        return Question.objects.create(
            quiz=self.quiz,
            question_text=text,
            option_a="Option A",
            option_b="Option B",
            option_c="Option C",
            option_d="Option D",
            correct_answer=correct_answer,
            difficulty=difficulty,
        )

    def get_adaptive_quiz(self):
        return self.client.get(
            (
                "/api/quizzes/adaptive/"
                f"?topic={self.topic1.id}"
            )
        )

    def build_correct_submission(
        self,
        response,
    ):
        """
        Build a correct answer submission
        directly from the test database.

        The API itself does not expose
        correct_answer to students.
        """

        session_id = (
            response.data[
                "session"
            ]["id"]
        )

        session = AdaptiveQuizSession.objects.get(
            id=session_id
        )

        questions = (
            session.questions
            .all()
            .order_by("id")
        )

        answers = []

        for question in questions:
            answers.append(
                {
                    "question": question.id,
                    "answer": (
                        question.correct_answer
                        .strip()
                        .upper()
                    ),
                }
            )

        return {
            "session_id": str(
                session.id
            ),
            "answers": answers,
        }

    def submit_perfect_attempt(
        self,
        quiz_response,
    ):
        payload = self.build_correct_submission(
            quiz_response
        )

        return self.client.post(
            "/api/quizzes/adaptive/submit/",
            payload,
            format="json",
        )

    # =========================================================
    # TEST 1
    # NEW TOPIC STARTS WITH EASY QUESTIONS
    # =========================================================

    def test_new_topic_starts_with_easy_questions(
        self
    ):
        response = self.get_adaptive_quiz()

        # GET request should return 200 OK.
        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data[
                "mastery"
            ]["level"],
            "not_started",
        )

        self.assertEqual(
            response.data[
                "adaptive_selection"
            ]["difficulty_value"],
            1,
        )

        self.assertEqual(
            response.data[
                "adaptive_selection"
            ]["difficulty"],
            "easy",
        )

        self.assertEqual(
            len(
                response.data[
                    "questions"
                ]
            ),
            3,
        )

    # =========================================================
    # TEST 2
    # EASY PERFECT SCORE -> DEVELOPING
    # =========================================================

    def test_easy_perfect_score_only_reaches_developing(
        self
    ):
        quiz_response = self.get_adaptive_quiz()

        response = self.submit_perfect_attempt(
            quiz_response
        )

        # POST creates QuizAttempt, so 201 Created.
        self.assertEqual(
            response.status_code,
            201,
        )

        mastery = response.data[
            "mastery_after"
        ]

        self.assertEqual(
            mastery["correct"],
            3,
        )

        self.assertEqual(
            mastery["total"],
            3,
        )

        self.assertEqual(
            mastery["mastery_score"],
            100.0,
        )

        # Easy evidence alone must not
        # produce good/strong mastery.
        self.assertEqual(
            mastery["level"],
            "developing",
        )

        self.assertEqual(
            response.data[
                "next_adaptive_difficulty"
            ]["value"],
            2,
        )

    # =========================================================
    # TEST 3
    # MEDIUM EVIDENCE -> GOOD
    # =========================================================

    def test_medium_evidence_reaches_good(
        self
    ):

        # -----------------------------------------------------
        # EASY ATTEMPT
        # -----------------------------------------------------

        easy_quiz = self.get_adaptive_quiz()

        easy_result = self.submit_perfect_attempt(
            easy_quiz
        )

        self.assertEqual(
            easy_result.status_code,
            201,
        )

        self.assertEqual(
            easy_result.data[
                "mastery_after"
            ]["level"],
            "developing",
        )

        # -----------------------------------------------------
        # NEXT QUIZ SHOULD BE MEDIUM
        # -----------------------------------------------------

        medium_quiz = self.get_adaptive_quiz()

        self.assertEqual(
            medium_quiz.status_code,
            200,
        )

        self.assertEqual(
            medium_quiz.data[
                "adaptive_selection"
            ]["difficulty_value"],
            2,
        )

        # -----------------------------------------------------
        # MEDIUM ATTEMPT
        # -----------------------------------------------------

        medium_result = (
            self.submit_perfect_attempt(
                medium_quiz
            )
        )

        self.assertEqual(
            medium_result.status_code,
            201,
        )

        mastery = medium_result.data[
            "mastery_after"
        ]

        self.assertEqual(
            mastery["correct"],
            6,
        )

        self.assertEqual(
            mastery["total"],
            6,
        )

        self.assertEqual(
            mastery["level"],
            "good",
        )

        # A good student should now receive
        # hard questions.
        self.assertEqual(
            medium_result.data[
                "next_adaptive_difficulty"
            ]["value"],
            3,
        )

    # =========================================================
    # TEST 4
    # HARD EVIDENCE -> STRONG
    # =========================================================

    def test_hard_evidence_reaches_strong(
        self
    ):

        # -----------------------------------------------------
        # EASY
        # -----------------------------------------------------

        easy_quiz = self.get_adaptive_quiz()

        easy_result = (
            self.submit_perfect_attempt(
                easy_quiz
            )
        )

        self.assertEqual(
            easy_result.status_code,
            201,
        )

        # -----------------------------------------------------
        # MEDIUM
        # -----------------------------------------------------

        medium_quiz = self.get_adaptive_quiz()

        medium_result = (
            self.submit_perfect_attempt(
                medium_quiz
            )
        )

        self.assertEqual(
            medium_result.status_code,
            201,
        )

        # -----------------------------------------------------
        # HARD
        # -----------------------------------------------------

        hard_quiz = self.get_adaptive_quiz()

        self.assertEqual(
            hard_quiz.status_code,
            200,
        )

        self.assertEqual(
            hard_quiz.data[
                "adaptive_selection"
            ]["difficulty_value"],
            3,
        )

        hard_result = (
            self.submit_perfect_attempt(
                hard_quiz
            )
        )

        self.assertEqual(
            hard_result.status_code,
            201,
        )

        mastery = hard_result.data[
            "mastery_after"
        ]

        self.assertEqual(
            mastery["correct"],
            9,
        )

        self.assertEqual(
            mastery["total"],
            9,
        )

        self.assertEqual(
            mastery["attempt_count"],
            3,
        )

        self.assertEqual(
            mastery["mastery_score"],
            100.0,
        )

        self.assertEqual(
            mastery["level"],
            "strong",
        )

        difficulty_performance = mastery[
            "difficulty_performance"
        ]

        self.assertEqual(
            difficulty_performance[
                "easy"
            ]["correct"],
            3,
        )

        self.assertEqual(
            difficulty_performance[
                "easy"
            ]["total"],
            3,
        )

        self.assertEqual(
            difficulty_performance[
                "medium"
            ]["correct"],
            3,
        )

        self.assertEqual(
            difficulty_performance[
                "medium"
            ]["total"],
            3,
        )

        self.assertEqual(
            difficulty_performance[
                "hard"
            ]["correct"],
            3,
        )

        self.assertEqual(
            difficulty_performance[
                "hard"
            ]["total"],
            3,
        )

    # =========================================================
    # TEST 5
    # NEXT TOPIC IS LOCKED
    # =========================================================

    def test_next_topic_locked_before_previous_is_strong(
        self
    ):
        response = self.client.get(
            (
                "/api/quizzes/adaptive/"
                f"?topic={self.topic2.id}"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            response.data["error"],
            "This topic is locked.",
        )

    # =========================================================
    # TEST 6
    # STRONG TOPIC UNLOCKS NEXT TOPIC
    # =========================================================

    def test_strong_topic_unlocks_next_topic(
        self
    ):

        # -----------------------------------------------------
        # EASY
        # -----------------------------------------------------

        easy_quiz = self.get_adaptive_quiz()

        easy_result = (
            self.submit_perfect_attempt(
                easy_quiz
            )
        )

        self.assertEqual(
            easy_result.status_code,
            201,
        )

        # -----------------------------------------------------
        # MEDIUM
        # -----------------------------------------------------

        medium_quiz = self.get_adaptive_quiz()

        medium_result = (
            self.submit_perfect_attempt(
                medium_quiz
            )
        )

        self.assertEqual(
            medium_result.status_code,
            201,
        )

        # -----------------------------------------------------
        # HARD
        # -----------------------------------------------------

        hard_quiz = self.get_adaptive_quiz()

        hard_result = (
            self.submit_perfect_attempt(
                hard_quiz
            )
        )

        self.assertEqual(
            hard_result.status_code,
            201,
        )

        self.assertEqual(
            hard_result.data[
                "mastery_after"
            ]["level"],
            "strong",
        )

        # -----------------------------------------------------
        # TOPIC 2 SHOULD NOW BE UNLOCKED
        # -----------------------------------------------------
        #
        # Topic 2 intentionally has no quiz.
        # It may therefore return 404.
        #
        # The important condition is that
        # it must NOT return the "locked"
        # 403 response.
        # -----------------------------------------------------

        topic2_response = self.client.get(
            (
                "/api/quizzes/adaptive/"
                f"?topic={self.topic2.id}"
            )
        )

        self.assertNotEqual(
            topic2_response.status_code,
            403,
        )

    # =========================================================
    # TEST 7
    # COMPLETED SESSION CANNOT BE SUBMITTED TWICE
    # =========================================================

    def test_completed_session_cannot_be_submitted_twice(
        self
    ):
        quiz_response = self.get_adaptive_quiz()

        self.assertEqual(
            quiz_response.status_code,
            200,
        )

        payload = self.build_correct_submission(
            quiz_response
        )

        # -----------------------------------------------------
        # FIRST SUBMISSION
        # -----------------------------------------------------

        first_response = self.client.post(
            "/api/quizzes/adaptive/submit/",
            payload,
            format="json",
        )

        # A new QuizAttempt is created.
        self.assertEqual(
            first_response.status_code,
            201,
        )

        self.assertEqual(
            QuizAttempt.objects.count(),
            1,
        )

        # -----------------------------------------------------
        # SECOND SUBMISSION OF SAME SESSION
        # -----------------------------------------------------

        second_response = self.client.post(
            "/api/quizzes/adaptive/submit/",
            payload,
            format="json",
        )

        # Completed session must be rejected.
        self.assertIn(
            second_response.status_code,
            [400, 409],
        )

        # Most importantly, the retry must
        # NOT create another QuizAttempt.
        self.assertEqual(
            QuizAttempt.objects.count(),
            1,
        )