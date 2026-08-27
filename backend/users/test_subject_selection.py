from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from courses.models import (
    AcademicYear,
    Board,
    Grade,
    Subject,
)

from users.models import Student


class StudentSubjectSelectionTests(APITestCase):

    def setUp(self):

        self.board = Board.objects.create(
            code="KSEAB-TEST",
            name="KSEAB Test Board",
            state="Karnataka",
            country="India",
        )

        self.academic_year = (
            AcademicYear.objects.create(
                board=self.board,
                name="2026-27",
            )
        )

        self.grade = Grade.objects.create(
            academic_year=self.academic_year,
            name="SSLC Class 10",
            level=10,
        )

        self.maths = Subject.objects.create(
            grade=self.grade,
            name="Mathematics",
            subject_type="core",
            language="English",
            display_order=1,
        )

        self.science = Subject.objects.create(
            grade=self.grade,
            name="Science",
            subject_type="core",
            language="English",
            display_order=2,
        )

        self.social_science = Subject.objects.create(
            grade=self.grade,
            name="Social Science",
            subject_type="core",
            language="English",
            display_order=3,
        )

        self.kannada_first = Subject.objects.create(
            grade=self.grade,
            name="Kannada",
            subject_type="first_language",
            language="Kannada",
            display_order=10,
        )

        self.english_second = Subject.objects.create(
            grade=self.grade,
            name="English",
            subject_type="second_language",
            language="English",
            display_order=30,
        )

        self.hindi_third = Subject.objects.create(
            grade=self.grade,
            name="Hindi",
            subject_type="third_language",
            language="Hindi",
            display_order=40,
        )

        self.it_optional = Subject.objects.create(
            grade=self.grade,
            name="Information Technology",
            subject_type="optional",
            language="English",
            is_optional=True,
            display_order=60,
        )

        self.user = User.objects.create_user(
            username="subjectstudent",
            password="TestPass123!",
            email="subject@example.com",
        )

        self.student = Student.objects.create(
            user=self.user,
            grade=self.grade,
            school="Demo School",
            preferred_language="English",
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_available_subjects_are_returned(self):

        response = self.client.get(
            "/api/auth/subjects/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["core_subjects"]),
            3,
        )

        self.assertEqual(
            len(response.data["first_languages"]),
            1,
        )

        self.assertEqual(
            len(response.data["second_languages"]),
            1,
        )

        self.assertEqual(
            len(response.data["third_languages"]),
            1,
        )

    def test_student_can_select_languages(self):

        response = self.client.post(
            "/api/auth/subjects/",
            {
                "first_language": (
                    self.kannada_first.id
                ),
                "second_language": (
                    self.english_second.id
                ),
                "third_language": (
                    self.hindi_third.id
                ),
                "optional_subjects": [],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        selected_ids = set(
            self.student.selected_subjects.values_list(
                "id",
                flat=True,
            )
        )

        expected_ids = {
            self.maths.id,
            self.science.id,
            self.social_science.id,
            self.kannada_first.id,
            self.english_second.id,
            self.hindi_third.id,
        }

        self.assertEqual(
            selected_ids,
            expected_ids,
        )

    def test_core_subjects_are_added_automatically(self):

        self.client.post(
            "/api/auth/subjects/",
            {
                "first_language": (
                    self.kannada_first.id
                ),
                "second_language": (
                    self.english_second.id
                ),
                "third_language": (
                    self.hindi_third.id
                ),
                "optional_subjects": [],
            },
            format="json",
        )

        selected = (
            self.student.selected_subjects.all()
        )

        self.assertTrue(
            selected.filter(
                id=self.maths.id
            ).exists()
        )

        self.assertTrue(
            selected.filter(
                id=self.science.id
            ).exists()
        )

        self.assertTrue(
            selected.filter(
                id=self.social_science.id
            ).exists()
        )

    def test_optional_subject_can_be_selected(self):

        response = self.client.post(
            "/api/auth/subjects/",
            {
                "first_language": (
                    self.kannada_first.id
                ),
                "second_language": (
                    self.english_second.id
                ),
                "third_language": (
                    self.hindi_third.id
                ),
                "optional_subjects": [
                    self.it_optional.id
                ],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            self.student.selected_subjects.filter(
                id=self.it_optional.id
            ).exists()
        )

    def test_student_without_grade_is_rejected(self):

        self.student.grade = None
        self.student.save(
            update_fields=["grade"]
        )

        response = self.client.get(
            "/api/auth/subjects/"
        )

        self.assertEqual(
            response.status_code,
            400,
        )