from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from courses.models import (
    AcademicYear,
    Board,
    Grade,
)

from users.models import (
    Student,
    Teacher,
)


class AuthenticationAndTeacherTests(APITestCase):

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

        self.grade10 = Grade.objects.create(
            academic_year=self.academic_year,
            name="SSLC Class 10",
            level=10,
            description="Class 10",
        )

        self.grade9 = Grade.objects.create(
            academic_year=self.academic_year,
            name="Class 9",
            level=9,
            description="Class 9",
        )

        # =====================================================
        # TEACHER
        # =====================================================

        self.teacher_user = User.objects.create_user(
            username="teacher1",
            password="Teacher@123",
            email="teacher@example.com",
        )

        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            school="Demo High School",
        )

        # =====================================================
        # SAME-SCHOOL STUDENT 1
        # =====================================================

        self.student_user = User.objects.create_user(
            username="student1",
            password="Student@123",
            email="student1@example.com",
        )

        self.student = Student.objects.create(
            user=self.student_user,
            grade=self.grade10,
            school="Demo High School",
            preferred_language="English",
        )

        # =====================================================
        # SAME-SCHOOL STUDENT 2
        # =====================================================

        self.student2_user = User.objects.create_user(
            username="student2",
            password="Student@123",
            email="student2@example.com",
        )

        self.student2 = Student.objects.create(
            user=self.student2_user,
            grade=self.grade10,
            school="Demo High School",
            preferred_language="English",
        )

        # =====================================================
        # DIFFERENT-SCHOOL STUDENT
        # =====================================================

        self.other_user = User.objects.create_user(
            username="otherstudent",
            password="Student@123",
            email="other@example.com",
        )

        self.other_student = Student.objects.create(
            user=self.other_user,
            grade=self.grade10,
            school="Other High School",
            preferred_language="English",
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def authenticate_student(self):
        self.client.force_authenticate(
            user=self.student_user
        )

    def authenticate_teacher(self):
        self.client.force_authenticate(
            user=self.teacher_user
        )

    # =========================================================
    # TEST 1
    # STUDENT LOGIN SUCCESS
    # =========================================================

    def test_student_login_success(self):

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "student1",
                "password": "Student@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["message"],
            "Login successful.",
        )

        self.assertIn(
            "token",
            response.data,
        )

        self.assertIn(
            "student",
            response.data,
        )

        self.assertTrue(
            Token.objects.filter(
                user=self.student_user
            ).exists()
        )

    # =========================================================
    # TEST 2
    # INVALID STUDENT LOGIN
    # =========================================================

    def test_invalid_student_credentials_are_rejected(self):

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "student1",
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.data["error"],
            "Invalid username or password.",
        )

    # =========================================================
    # TEST 3
    # TEACHER CANNOT USE STUDENT LOGIN
    # =========================================================

    def test_teacher_account_cannot_use_student_login(self):

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "teacher1",
                "password": "Teacher@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            response.data["error"],
            (
                "This account is not "
                "registered as a student."
            ),
        )

    # =========================================================
    # TEST 4
    # TEACHER LOGIN SUCCESS
    # =========================================================

    def test_teacher_login_success(self):

        response = self.client.post(
            "/api/auth/teacher/login/",
            {
                "username": "teacher1",
                "password": "Teacher@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["message"],
            "Teacher login successful.",
        )

        self.assertIn(
            "token",
            response.data,
        )

        self.assertIn(
            "teacher",
            response.data,
        )

        self.assertEqual(
            response.data[
                "teacher"
            ]["username"],
            "teacher1",
        )

        self.assertEqual(
            response.data[
                "teacher"
            ]["school"],
            "Demo High School",
        )

        self.assertTrue(
            Token.objects.filter(
                user=self.teacher_user
            ).exists()
        )

    # =========================================================
    # TEST 5
    # INVALID TEACHER LOGIN
    # =========================================================

    def test_invalid_teacher_credentials_are_rejected(self):

        response = self.client.post(
            "/api/auth/teacher/login/",
            {
                "username": "teacher1",
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            response.data["error"],
            "Invalid username or password.",
        )

    # =========================================================
    # TEST 6
    # STUDENT CANNOT USE TEACHER LOGIN
    # =========================================================

    def test_student_account_cannot_use_teacher_login(self):

        response = self.client.post(
            "/api/auth/teacher/login/",
            {
                "username": "student1",
                "password": "Student@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            response.data["error"],
            (
                "This account is not "
                "registered as a teacher."
            ),
        )

    # =========================================================
    # TEST 7
    # STUDENT PROFILE
    # =========================================================

    def test_student_can_access_own_profile(self):

        self.authenticate_student()

        response = self.client.get(
            "/api/auth/profile/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # =========================================================
    # TEST 8
    # TEACHER CANNOT ACCESS STUDENT PROFILE
    # =========================================================

    def test_teacher_cannot_access_student_profile(self):

        self.authenticate_teacher()

        response = self.client.get(
            "/api/auth/profile/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            response.data["error"],
            "Student profile not found.",
        )

    # =========================================================
    # TEST 9
    # STUDENT BLOCKED FROM TEACHER DASHBOARD
    # =========================================================

    def test_student_cannot_access_teacher_dashboard(self):

        self.authenticate_student()

        response = self.client.get(
            "/api/teacher/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            response.data["error"],
            (
                "Only teachers can access "
                "the teacher dashboard."
            ),
        )

    # =========================================================
    # TEST 10
    # TEACHER DASHBOARD
    # =========================================================

    def test_teacher_can_access_dashboard(self):

        self.authenticate_teacher()

        response = self.client.get(
            "/api/teacher/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        # -----------------------------------------------------
        # TEACHER INFORMATION
        # -----------------------------------------------------

        self.assertEqual(
            response.data[
                "teacher"
            ]["username"],
            "teacher1",
        )

        self.assertEqual(
            response.data[
                "teacher"
            ]["school"],
            "Demo High School",
        )

        # -----------------------------------------------------
        # DASHBOARD OVERVIEW
        # -----------------------------------------------------

        overview = response.data[
            "overview"
        ]

        self.assertEqual(
            overview[
                "total_students"
            ],
            2,
        )

        self.assertEqual(
            overview[
                "active_students"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "completed_students"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "students_needing_help"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "total_quiz_attempts"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "average_completion_percentage"
            ],
            0,
        )

        self.assertEqual(
            overview[
                "average_quiz_accuracy"
            ],
            0,
        )

        # Teacher must only receive
        # students from Demo High School.

        self.assertEqual(
            len(
                response.data[
                    "students"
                ]
            ),
            2,
        )

    # =========================================================
    # TEST 11
    # TEACHER STUDENT LIST IS SCHOOL-SCOPED
    # =========================================================

    def test_teacher_student_list_is_school_scoped(self):

        self.authenticate_teacher()

        response = self.client.get(
            "/api/teacher/students/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

        self.assertEqual(
            len(
                response.data[
                    "students"
                ]
            ),
            2,
        )

        usernames = [
            student["username"]
            for student
            in response.data["students"]
        ]

        self.assertIn(
            "student1",
            usernames,
        )

        self.assertIn(
            "student2",
            usernames,
        )

        self.assertNotIn(
            "otherstudent",
            usernames,
        )

    # =========================================================
    # TEST 12
    # SAME-SCHOOL STUDENT PROGRESS
    # =========================================================

    def test_teacher_can_access_same_school_student_progress(
        self
    ):

        self.authenticate_teacher()

        response = self.client.get(
            (
                "/api/teacher/students/"
                f"{self.student.id}/progress/"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data[
                "student"
            ]["student_id"],
            self.student.id,
        )

        self.assertEqual(
            response.data[
                "student"
            ]["username"],
            "student1",
        )

    # =========================================================
    # TEST 13
    # OTHER-SCHOOL STUDENT BLOCKED
    # =========================================================

    def test_teacher_cannot_access_other_school_student_progress(
        self
    ):

        self.authenticate_teacher()

        response = self.client.get(
            (
                "/api/teacher/students/"
                f"{self.other_student.id}/progress/"
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            response.data["error"],
            (
                "Student not found in "
                "your school."
            ),
        )

    # =========================================================
    # TEST 14
    # TEACHER WEAK TOPICS ENDPOINT
    # =========================================================

    def test_teacher_can_access_weak_topics(self):

        self.authenticate_teacher()

        response = self.client.get(
            "/api/teacher/weak-topics/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "count",
            response.data,
        )

        self.assertIn(
            "weak_topics",
            response.data,
        )

        # No topics or attempts have been
        # created in this test fixture.

        self.assertEqual(
            response.data["count"],
            0,
        )

    # =========================================================
    # TEST 15
    # TEACHER RECENT ATTEMPTS
    # =========================================================

    def test_teacher_can_access_recent_attempts(self):

        self.authenticate_teacher()

        response = self.client.get(
            "/api/teacher/recent-attempts/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "count",
            response.data,
        )

        self.assertIn(
            "attempts",
            response.data,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

        self.assertEqual(
            response.data["attempts"],
            [],
        )

    # =========================================================
    # TEST 16
    # TEACHER CAN ASSIGN STUDENT GRADE
    # =========================================================

    def test_teacher_can_assign_student_grade(self):

        self.authenticate_teacher()

        response = self.client.post(
            (
                "/api/auth/students/"
                f"{self.student.id}/grade/"
            ),
            {
                "grade": self.grade9.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.student.refresh_from_db()

        self.assertEqual(
            self.student.grade,
            self.grade9,
        )

        self.assertEqual(
            response.data["message"],
            (
                "Student grade assigned "
                "successfully."
            ),
        )

    # =========================================================
    # TEST 17
    # STUDENT CANNOT ASSIGN GRADES
    # =========================================================

    def test_student_cannot_assign_grade(self):

        self.authenticate_student()

        response = self.client.post(
            (
                "/api/auth/students/"
                f"{self.student2.id}/grade/"
            ),
            {
                "grade": self.grade9.id,
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [401, 403],
        )

        # Ensure the grade was not changed.

        self.student2.refresh_from_db()

        self.assertEqual(
            self.student2.grade,
            self.grade10,
        )

    # =========================================================
    # TEST 18
    # UNAUTHENTICATED USER BLOCKED
    # =========================================================

    def test_unauthenticated_user_cannot_access_teacher_dashboard(
        self
    ):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            "/api/teacher/dashboard/"
        )

        self.assertIn(
            response.status_code,
            [401, 403],
        )