from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from courses.models import (
    AcademicYear,
    Board,
    Chapter,
    Grade,
    Subject,
    Topic,
)

from progress.models import (
    Answer,
    QuizAttempt,
)

from quizzes.models import (
    Question,
    Quiz,
)

from users.models import Student


class ProgressSystemTests(APITestCase):

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
            description="Progress test chapter",
        )

        # =====================================================
        # TOPICS
        # =====================================================

        self.topic1 = Topic.objects.create(
            chapter=self.chapter,
            name="Topic 1",
            description="First topic",
            difficulty=1,
        )

        self.topic2 = Topic.objects.create(
            chapter=self.chapter,
            name="Topic 2",
            description="Second topic",
            difficulty=1,
        )

        # =====================================================
        # QUIZZES
        # =====================================================

        self.quiz1 = Quiz.objects.create(
            topic=self.topic1,
            title="Topic 1 Quiz",
            description="Quiz for topic 1",
        )

        self.quiz2 = Quiz.objects.create(
            topic=self.topic2,
            title="Topic 2 Quiz",
            description="Quiz for topic 2",
        )

        # =====================================================
        # QUESTIONS FOR TOPIC 1
        # =====================================================

        self.topic1_easy = (
            self.create_question_group(
                quiz=self.quiz1,
                difficulty=1,
                prefix="Topic1 Easy",
            )
        )

        self.topic1_medium = (
            self.create_question_group(
                quiz=self.quiz1,
                difficulty=2,
                prefix="Topic1 Medium",
            )
        )

        self.topic1_hard = (
            self.create_question_group(
                quiz=self.quiz1,
                difficulty=3,
                prefix="Topic1 Hard",
            )
        )

        # =====================================================
        # QUESTIONS FOR TOPIC 2
        # =====================================================

        self.topic2_easy = (
            self.create_question_group(
                quiz=self.quiz2,
                difficulty=1,
                prefix="Topic2 Easy",
            )
        )

        self.topic2_medium = (
            self.create_question_group(
                quiz=self.quiz2,
                difficulty=2,
                prefix="Topic2 Medium",
            )
        )

        self.topic2_hard = (
            self.create_question_group(
                quiz=self.quiz2,
                difficulty=3,
                prefix="Topic2 Hard",
            )
        )

        # =====================================================
        # STUDENT
        # =====================================================

        self.user = User.objects.create_user(
            username="progressstudent",
            password="Student@123",
            email="student@example.com",
        )

        self.student = Student.objects.create(
            user=self.user,
            grade=self.grade,
            school="Demo High School",
            preferred_language="English",
        )

        # Authenticate all API requests as this student.
        self.client.force_authenticate(
            user=self.user
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def create_question_group(
        self,
        quiz,
        difficulty,
        prefix,
    ):
        """
        Create three questions for one
        difficulty level.
        """

        correct_answers = [
            "A",
            "B",
            "C",
        ]

        questions = []

        for index in range(3):

            question = Question.objects.create(
                quiz=quiz,
                question_text=(
                    f"{prefix} Question "
                    f"{index + 1}"
                ),
                option_a="Option A",
                option_b="Option B",
                option_c="Option C",
                option_d="Option D",
                correct_answer=(
                    correct_answers[index]
                ),
                difficulty=difficulty,
            )

            questions.append(
                question
            )

        return questions

    def create_perfect_attempt(
        self,
        quiz,
        questions,
    ):
        """
        Create a perfect 3/3 attempt and
        corresponding Answer records.
        """

        attempt = QuizAttempt.objects.create(
            student=self.student,
            quiz=quiz,
            score=3,
            total_questions=3,
        )

        for question in questions:

            Answer.objects.create(
                attempt=attempt,
                question=question,
                selected_answer=(
                    question.correct_answer
                ),
                is_correct=True,
            )

        return attempt

    def make_topic1_strong(self):
        """
        Give Topic 1 perfect Easy,
        Medium and Hard evidence.
        """

        self.create_perfect_attempt(
            self.quiz1,
            self.topic1_easy,
        )

        self.create_perfect_attempt(
            self.quiz1,
            self.topic1_medium,
        )

        self.create_perfect_attempt(
            self.quiz1,
            self.topic1_hard,
        )

    def make_topic2_strong(self):
        """
        Give Topic 2 perfect Easy,
        Medium and Hard evidence.
        """

        self.create_perfect_attempt(
            self.quiz2,
            self.topic2_easy,
        )

        self.create_perfect_attempt(
            self.quiz2,
            self.topic2_medium,
        )

        self.create_perfect_attempt(
            self.quiz2,
            self.topic2_hard,
        )

    # =========================================================
    # TEST 1
    # NEW STUDENT LEARNING PATH
    # =========================================================

    def test_new_student_learning_path(
        self
    ):
        response = self.client.get(
            "/api/progress/learning-path/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        summary = response.data[
            "summary"
        ]

        self.assertEqual(
            summary["total_topics"],
            2,
        )

        self.assertEqual(
            summary["completed"],
            0,
        )

        self.assertEqual(
            summary["available"],
            1,
        )

        self.assertEqual(
            summary["locked"],
            1,
        )

        self.assertEqual(
            summary[
                "completion_percentage"
            ],
            0,
        )

        topics = response.data[
            "topics"
        ]

        # Topic 1 is the first topic,
        # therefore always available.

        self.assertEqual(
            topics[0]["topic_id"],
            self.topic1.id,
        )

        self.assertEqual(
            topics[0]["status"],
            "available",
        )

        self.assertTrue(
            topics[0]["unlocked"]
        )

        self.assertEqual(
            topics[0]["level"],
            "not_started",
        )

        # Topic 2 requires Topic 1
        # to become strong.

        self.assertEqual(
            topics[1]["topic_id"],
            self.topic2.id,
        )

        self.assertEqual(
            topics[1]["status"],
            "locked",
        )

        self.assertFalse(
            topics[1]["unlocked"]
        )

    # =========================================================
    # TEST 2
    # NEW STUDENT CHAPTER PROGRESS
    # =========================================================

    def test_new_student_chapter_progress(
        self
    ):
        response = self.client.get(
            "/api/progress/chapter-progress/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        summary = response.data[
            "summary"
        ]

        self.assertEqual(
            summary["total_chapters"],
            1,
        )

        self.assertEqual(
            summary[
                "completed_chapters"
            ],
            0,
        )

        self.assertEqual(
            summary[
                "in_progress_chapters"
            ],
            0,
        )

        self.assertEqual(
            summary[
                "not_started_chapters"
            ],
            1,
        )

        self.assertEqual(
            summary[
                "overall_completion_percentage"
            ],
            0,
        )

        chapter = response.data[
            "chapters"
        ][0]

        self.assertEqual(
            chapter["status"],
            "not_started",
        )

        self.assertEqual(
            chapter["total_topics"],
            2,
        )

        self.assertEqual(
            chapter["started_topics"],
            0,
        )

        self.assertEqual(
            chapter["completed_topics"],
            0,
        )

        self.assertEqual(
            chapter["remaining_topics"],
            2,
        )

        self.assertEqual(
            chapter[
                "completion_percentage"
            ],
            0,
        )

    # =========================================================
    # TEST 3
    # NEW STUDENT DASHBOARD
    # =========================================================

    def test_new_student_dashboard(
        self
    ):
        response = self.client.get(
            "/api/progress/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data[
                "student"
            ]["username"],
            "progressstudent",
        )

        overview = response.data[
            "overview"
        ]

        self.assertEqual(
            overview["total_topics"],
            2,
        )

        self.assertEqual(
            overview[
                "completed_topics"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "available_topics"
            ],
            1,
        )

        self.assertEqual(
            overview[
                "locked_topics"
            ],
            1,
        )

        self.assertEqual(
            overview[
                "topic_completion_percentage"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "total_chapters"
            ],
            1,
        )

        self.assertEqual(
            overview[
                "completed_chapters"
            ],
            0,
        )

        # Current dashboard implementation
        # calls the first unlocked topic
        # "continue_learning".

        self.assertEqual(
            response.data["status"],
            "learning_in_progress",
        )

        continue_learning = (
            response.data[
                "continue_learning"
            ]
        )

        self.assertIsNotNone(
            continue_learning
        )

        self.assertEqual(
            continue_learning[
                "topic_id"
            ],
            self.topic1.id,
        )

        self.assertEqual(
            continue_learning[
                "status"
            ],
            "available",
        )

        self.assertEqual(
            response.data[
                "recent_activity"
            ],
            [],
        )

    # =========================================================
    # TEST 4
    # STRONG TOPIC 1 UNLOCKS TOPIC 2
    # =========================================================

    def test_strong_topic_unlocks_next_topic(
        self
    ):
        self.make_topic1_strong()

        response = self.client.get(
            "/api/progress/learning-path/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        summary = response.data[
            "summary"
        ]

        self.assertEqual(
            summary["completed"],
            1,
        )

        self.assertEqual(
            summary["available"],
            1,
        )

        self.assertEqual(
            summary["locked"],
            0,
        )

        self.assertEqual(
            summary[
                "completion_percentage"
            ],
            50.0,
        )

        topics = response.data[
            "topics"
        ]

        topic1 = topics[0]
        topic2 = topics[1]

        self.assertEqual(
            topic1["status"],
            "completed",
        )

        self.assertEqual(
            topic1["level"],
            "strong",
        )

        self.assertTrue(
            topic1["unlocked"]
        )

        self.assertEqual(
            topic2["status"],
            "available",
        )

        self.assertTrue(
            topic2["unlocked"]
        )

        self.assertEqual(
            topic2["level"],
            "not_started",
        )

        self.assertEqual(
            topic2[
                "previous_topic"
            ]["id"],
            self.topic1.id,
        )

        self.assertEqual(
            topic2[
                "previous_topic"
            ]["level"],
            "strong",
        )

    # =========================================================
    # TEST 5
    # PARTIAL CHAPTER -> IN PROGRESS
    # =========================================================

    def test_partial_chapter_is_in_progress(
        self
    ):
        self.make_topic1_strong()

        response = self.client.get(
            "/api/progress/chapter-progress/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        summary = response.data[
            "summary"
        ]

        self.assertEqual(
            summary[
                "completed_chapters"
            ],
            0,
        )

        self.assertEqual(
            summary[
                "in_progress_chapters"
            ],
            1,
        )

        self.assertEqual(
            summary[
                "not_started_chapters"
            ],
            0,
        )

        chapter = response.data[
            "chapters"
        ][0]

        self.assertEqual(
            chapter["status"],
            "in_progress",
        )

        self.assertEqual(
            chapter["total_topics"],
            2,
        )

        self.assertEqual(
            chapter["started_topics"],
            1,
        )

        self.assertEqual(
            chapter["completed_topics"],
            1,
        )

        self.assertEqual(
            chapter["remaining_topics"],
            1,
        )

        self.assertEqual(
            chapter[
                "completion_percentage"
            ],
            50.0,
        )

    # =========================================================
    # TEST 6
    # DASHBOARD CONTINUES TO TOPIC 2
    # =========================================================

    def test_dashboard_moves_continue_learning_to_next_topic(
        self
    ):
        self.make_topic1_strong()

        response = self.client.get(
            "/api/progress/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        overview = response.data[
            "overview"
        ]

        self.assertEqual(
            overview[
                "completed_topics"
            ],
            1,
        )

        self.assertEqual(
            overview[
                "available_topics"
            ],
            1,
        )

        self.assertEqual(
            overview[
                "locked_topics"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "topic_completion_percentage"
            ],
            50.0,
        )

        self.assertEqual(
            overview[
                "in_progress_chapters"
            ],
            1,
        )

        continue_learning = (
            response.data[
                "continue_learning"
            ]
        )

        self.assertIsNotNone(
            continue_learning
        )

        self.assertEqual(
            continue_learning[
                "topic_id"
            ],
            self.topic2.id,
        )

        self.assertEqual(
            continue_learning[
                "topic_name"
            ],
            "Topic 2",
        )

        self.assertEqual(
            continue_learning[
                "action"
            ],
            "continue_learning",
        )

        self.assertEqual(
            response.data["status"],
            "learning_in_progress",
        )

    # =========================================================
    # TEST 7
    # ALL TOPICS STRONG -> CHAPTER COMPLETE
    # =========================================================

    def test_all_topics_strong_completes_chapter(
        self
    ):
        self.make_topic1_strong()
        self.make_topic2_strong()

        response = self.client.get(
            "/api/progress/chapter-progress/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        summary = response.data[
            "summary"
        ]

        self.assertEqual(
            summary[
                "total_chapters"
            ],
            1,
        )

        self.assertEqual(
            summary[
                "completed_chapters"
            ],
            1,
        )

        self.assertEqual(
            summary[
                "in_progress_chapters"
            ],
            0,
        )

        self.assertEqual(
            summary[
                "not_started_chapters"
            ],
            0,
        )

        self.assertEqual(
            summary[
                "overall_completion_percentage"
            ],
            100.0,
        )

        chapter = response.data[
            "chapters"
        ][0]

        self.assertEqual(
            chapter["status"],
            "completed",
        )

        self.assertEqual(
            chapter["completed_topics"],
            2,
        )

        self.assertEqual(
            chapter["remaining_topics"],
            0,
        )

        self.assertEqual(
            chapter[
                "completion_percentage"
            ],
            100.0,
        )

        self.assertEqual(
            chapter[
                "average_mastery"
            ],
            100.0,
        )

    # =========================================================
    # TEST 8
    # ALL TOPICS COMPLETE -> DASHBOARD COMPLETE
    # =========================================================

    def test_completed_dashboard_has_no_continue_learning(
        self
    ):
        self.make_topic1_strong()
        self.make_topic2_strong()

        response = self.client.get(
            "/api/progress/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        overview = response.data[
            "overview"
        ]

        self.assertEqual(
            overview[
                "total_topics"
            ],
            2,
        )

        self.assertEqual(
            overview[
                "completed_topics"
            ],
            2,
        )

        self.assertEqual(
            overview[
                "available_topics"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "locked_topics"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "topic_completion_percentage"
            ],
            100.0,
        )

        self.assertEqual(
            overview[
                "completed_chapters"
            ],
            1,
        )

        self.assertEqual(
            overview[
                "chapter_completion_percentage"
            ],
            100.0,
        )

        self.assertEqual(
            response.data["status"],
            "all_available_topics_completed",
        )

        self.assertIsNone(
            response.data[
                "continue_learning"
            ]
        )

    # =========================================================
    # TEST 9
    # RECENT ACTIVITY
    # =========================================================

    def test_dashboard_recent_activity(
        self
    ):
        attempt1 = (
            self.create_perfect_attempt(
                self.quiz1,
                self.topic1_easy,
            )
        )

        attempt2 = (
            self.create_perfect_attempt(
                self.quiz1,
                self.topic1_medium,
            )
        )

        response = self.client.get(
            "/api/progress/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        activity = response.data[
            "recent_activity"
        ]

        self.assertEqual(
            len(activity),
            2,
        )

        # Latest attempt should appear first.

        self.assertEqual(
            activity[0][
                "attempt_id"
            ],
            attempt2.id,
        )

        self.assertEqual(
            activity[1][
                "attempt_id"
            ],
            attempt1.id,
        )

        self.assertEqual(
            activity[0]["score"],
            3,
        )

        self.assertEqual(
            activity[0][
                "total_questions"
            ],
            3,
        )

        self.assertEqual(
            activity[0][
                "percentage"
            ],
            100.0,
        )

        self.assertEqual(
            activity[0][
                "topic_id"
            ],
            self.topic1.id,
        )

    # =========================================================
    # TEST 10
    # RECENT ACTIVITY LIMITED TO FIVE
    # =========================================================

    def test_dashboard_recent_activity_is_limited_to_five(
        self
    ):
        for _ in range(6):

            self.create_perfect_attempt(
                self.quiz1,
                self.topic1_easy,
            )

        response = self.client.get(
            "/api/progress/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        activity = response.data[
            "recent_activity"
        ]

        self.assertEqual(
            len(activity),
            5,
        )

    # =========================================================
    # TEST 11
    # UNAUTHENTICATED USER BLOCKED
    # =========================================================

    def test_unauthenticated_user_cannot_access_dashboard(
        self
    ):
        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            "/api/progress/dashboard/"
        )

        self.assertIn(
            response.status_code,
            [401, 403],
        )