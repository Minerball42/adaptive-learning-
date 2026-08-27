from django.contrib.auth import authenticate

from drf_spectacular.utils import extend_schema

from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Grade, Subject

from .models import Student, Teacher

from .serializers import (
    AssignStudentGradeRequestSerializer,
    AssignStudentGradeResponseSerializer,
    ErrorResponseSerializer,
    LoginRequestSerializer,
    StudentAvailableSubjectsResponseSerializer,
    StudentLoginResponseSerializer,
    StudentProfileSerializer,
    StudentRegisterResponseSerializer,
    StudentRegisterSerializer,
    StudentSelectedSubjectSerializer,
    StudentSubjectSelectionRequestSerializer,
    StudentSubjectSelectionResponseSerializer,
    TeacherLoginResponseSerializer,
)


# ============================================================
# STUDENT REGISTRATION
# ============================================================

class StudentRegisterView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Register a student",
        description=(
            "Create a new student account and return "
            "an authentication token."
        ),
        request=StudentRegisterSerializer,
        responses={
            201: StudentRegisterResponseSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def post(self, request):

        serializer = StudentRegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            student = serializer.save()

            token, _ = Token.objects.get_or_create(
                user=student.user
            )

            return Response(
                {
                    "message": (
                        "Student registered successfully."
                    ),
                    "token": token.key,
                    "student": StudentProfileSerializer(
                        student
                    ).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ============================================================
# STUDENT LOGIN
# ============================================================

class StudentLoginView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Student login",
        description=(
            "Authenticate a registered student "
            "and return a token."
        ),
        request=LoginRequestSerializer,
        responses={
            200: StudentLoginResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
    )
    def post(self, request):

        username = request.data.get(
            "username"
        )

        password = request.data.get(
            "password"
        )

        if not username or not password:

            return Response(
                {
                    "error": (
                        "Username and password are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:

            return Response(
                {
                    "error": (
                        "Invalid username or password."
                    )
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not hasattr(
            user,
            "student",
        ):

            return Response(
                {
                    "error": (
                        "This account is not registered "
                        "as a student."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _ = Token.objects.get_or_create(
            user=user
        )

        return Response(
            {
                "message": "Login successful.",
                "token": token.key,
                "student": StudentProfileSerializer(
                    user.student
                ).data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# TEACHER LOGIN
# ============================================================

class TeacherLoginView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Teacher login",
        description=(
            "Authenticate a registered teacher "
            "and return a token."
        ),
        request=LoginRequestSerializer,
        responses={
            200: TeacherLoginResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
    )
    def post(self, request):

        username = request.data.get(
            "username"
        )

        password = request.data.get(
            "password"
        )

        if not username or not password:

            return Response(
                {
                    "error": (
                        "Username and password "
                        "are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:

            return Response(
                {
                    "error": (
                        "Invalid username or password."
                    )
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not hasattr(
            user,
            "teacher",
        ):

            return Response(
                {
                    "error": (
                        "This account is not registered "
                        "as a teacher."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _ = Token.objects.get_or_create(
            user=user
        )

        teacher = user.teacher

        return Response(
            {
                "message": (
                    "Teacher login successful."
                ),
                "token": token.key,
                "teacher": {
                    "username": user.username,
                    "email": user.email,
                    "school": teacher.school,
                },
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# STUDENT PROFILE
# ============================================================

class StudentProfileView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Get student profile",
        description=(
            "Return the authenticated "
            "student's profile."
        ),
        responses={
            200: StudentProfileSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request):

        try:

            student = request.user.student

        except Student.DoesNotExist:

            return Response(
                {
                    "error": (
                        "Student profile not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            StudentProfileSerializer(
                student
            ).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# STUDENT SUBJECT SELECTION
# ============================================================

class StudentSubjectSelectionView(APIView):

    permission_classes = [IsAuthenticated]

    def get_student(
        self,
        request,
    ):

        try:

            return request.user.student

        except Student.DoesNotExist:

            return None

    @extend_schema(
        tags=["Authentication"],
        summary="Get available student subjects",
        description=(
            "Return core subjects, language subjects, "
            "optional subjects and current selections."
        ),
        responses={
            200: StudentAvailableSubjectsResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(
        self,
        request,
    ):

        student = self.get_student(
            request
        )

        if student is None:

            return Response(
                {
                    "error": (
                        "Student profile not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not student.grade:

            return Response(
                {
                    "error": (
                        "The student must have "
                        "a grade assigned first."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        subjects = Subject.objects.filter(
            grade=student.grade
        )

        core_subjects = subjects.filter(
            subject_type="core"
        )

        first_languages = subjects.filter(
            subject_type="first_language"
        )

        second_languages = subjects.filter(
            subject_type="second_language"
        )

        third_languages = subjects.filter(
            subject_type="third_language"
        )

        optional_subjects = subjects.filter(
            subject_type="optional"
        )

        return Response(
            {
                "grade": {
                    "id": student.grade.id,
                    "name": student.grade.name,
                },

                "core_subjects": (
                    StudentSelectedSubjectSerializer(
                        core_subjects,
                        many=True,
                    ).data
                ),

                "first_languages": (
                    StudentSelectedSubjectSerializer(
                        first_languages,
                        many=True,
                    ).data
                ),

                "second_languages": (
                    StudentSelectedSubjectSerializer(
                        second_languages,
                        many=True,
                    ).data
                ),

                "third_languages": (
                    StudentSelectedSubjectSerializer(
                        third_languages,
                        many=True,
                    ).data
                ),

                "optional_subjects": (
                    StudentSelectedSubjectSerializer(
                        optional_subjects,
                        many=True,
                    ).data
                ),

                "selected_subjects": (
                    StudentSelectedSubjectSerializer(
                        student.selected_subjects.all(),
                        many=True,
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Authentication"],
        summary="Select student subjects",
        description=(
            "Save the student's KSEAB subject "
            "selections. Core subjects are "
            "included automatically."
        ),
        request=StudentSubjectSelectionRequestSerializer,
        responses={
            200: StudentSubjectSelectionResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def post(
        self,
        request,
    ):

        student = self.get_student(
            request
        )

        if student is None:

            return Response(
                {
                    "error": (
                        "Student profile not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not student.grade:

            return Response(
                {
                    "error": (
                        "The student must have "
                        "a grade assigned first."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            StudentSubjectSelectionRequestSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        available_subjects = (
            Subject.objects.filter(
                grade=student.grade
            )
        )

        # Core subjects are always included.
        selected = list(
            available_subjects.filter(
                subject_type="core"
            )
        )

        errors = {}

        language_fields = [
            (
                "first_language",
                "first_language",
            ),
            (
                "second_language",
                "second_language",
            ),
            (
                "third_language",
                "third_language",
            ),
        ]

        for (
            field_name,
            subject_type,
        ) in language_fields:

            options = (
                available_subjects.filter(
                    subject_type=subject_type
                )
            )

            selected_id = data.get(
                field_name
            )

            if (
                options.exists()
                and
                not selected_id
            ):

                errors[field_name] = (
                    "This language selection "
                    "is required."
                )

                continue

            if selected_id:

                subject = options.filter(
                    id=selected_id
                ).first()

                if subject is None:

                    errors[field_name] = (
                        "Invalid subject for this "
                        "grade or language category."
                    )

                else:

                    selected.append(
                        subject
                    )

        optional_ids = data.get(
            "optional_subjects",
            []
        )

        for subject_id in optional_ids:

            subject = (
                available_subjects.filter(
                    id=subject_id
                ).first()
            )

            if subject is None:

                errors.setdefault(
                    "optional_subjects",
                    []
                ).append(
                    (
                        f"Subject {subject_id} "
                        "does not belong to "
                        "this grade."
                    )
                )

                continue

            if not (
                subject.subject_type == "optional"
                or
                subject.is_optional
            ):

                errors.setdefault(
                    "optional_subjects",
                    []
                ).append(
                    (
                        f"Subject {subject_id} "
                        "is not optional."
                    )
                )

                continue

            selected.append(
                subject
            )

        if errors:

            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        unique_subjects = {
            subject.id: subject
            for subject in selected
        }

        student.selected_subjects.set(
            unique_subjects.values()
        )

        return Response(
            {
                "message": (
                    "Student subjects selected "
                    "successfully."
                ),

                "selected_subjects": (
                    StudentSelectedSubjectSerializer(
                        student.selected_subjects.all(),
                        many=True,
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# TEACHER / ADMIN PERMISSION
# ============================================================

class IsTeacherOrAdmin(
    permissions.BasePermission
):

    def has_permission(
        self,
        request,
        view,
    ):

        if (
            not request.user
            or
            not request.user.is_authenticated
        ):

            return False

        if (
            request.user.is_staff
            or
            request.user.is_superuser
        ):

            return True

        return Teacher.objects.filter(
            user=request.user
        ).exists()


# ============================================================
# ASSIGN STUDENT GRADE
# ============================================================

class AssignStudentGradeView(APIView):

    permission_classes = [
        IsTeacherOrAdmin
    ]

    @extend_schema(
        tags=["Authentication"],
        summary="Assign grade to student",
        description=(
            "Allow a teacher or administrator "
            "to assign a grade to a student."
        ),
        request=AssignStudentGradeRequestSerializer,
        responses={
            200: AssignStudentGradeResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def post(
        self,
        request,
        student_id,
    ):

        try:

            student = Student.objects.get(
                id=student_id
            )

        except Student.DoesNotExist:

            return Response(
                {
                    "error": "Student not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        grade_id = request.data.get(
            "grade"
        )

        if not grade_id:

            return Response(
                {
                    "error": (
                        "Grade ID is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            grade = Grade.objects.get(
                id=grade_id
            )

        except Grade.DoesNotExist:

            return Response(
                {
                    "error": "Grade not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        student.grade = grade

        student.save(
            update_fields=[
                "grade"
            ]
        )

        return Response(
            {
                "message": (
                    "Student grade assigned "
                    "successfully."
                ),

                "student": (
                    StudentProfileSerializer(
                        student
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )