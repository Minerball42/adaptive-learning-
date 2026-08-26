from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)

from drf_spectacular.types import (
    OpenApiTypes,
)

from rest_framework import status

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response

from rest_framework.views import APIView


from users.models import Teacher

from .serializers import (
    ErrorResponseSerializer,
    TeacherDashboardResponseSerializer,
    TeacherRecentAttemptsResponseSerializer,
    TeacherStudentProgressResponseSerializer,
    TeacherStudentsResponseSerializer,
    TeacherWeakTopicsResponseSerializer,
)

from .teacher_services import (
    build_student_summary,
    build_teacher_dashboard,
    build_teacher_recent_attempts,
    build_teacher_student_progress,
    build_teacher_weak_topics,
    get_teacher_student,
    get_teacher_students,
)


# ============================================================
# HELPER
# ============================================================

def get_teacher_for_user(user):

    try:
        return user.teacher

    except Teacher.DoesNotExist:
        return None


# ============================================================
# TEACHER DASHBOARD
# ============================================================

class TeacherDashboardView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Teacher"
        ],

        summary=(
            "Get teacher dashboard"
        ),

        description=(
            "Return dashboard statistics and "
            "student summaries for students "
            "belonging to the teacher's school."
        ),

        responses={
            200: (
                TeacherDashboardResponseSerializer
            ),

            403: (
                ErrorResponseSerializer
            ),
        },
    )
    def get(
        self,
        request,
    ):

        teacher = get_teacher_for_user(
            request.user
        )

        if teacher is None:

            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "the teacher dashboard."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        return Response(
            build_teacher_dashboard(
                teacher
            ),
            status=(
                status.HTTP_200_OK
            ),
        )


# ============================================================
# TEACHER STUDENT LIST
# ============================================================

class TeacherStudentsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Teacher"
        ],

        summary=(
            "List teacher's students"
        ),

        description=(
            "Return students belonging to "
            "the authenticated teacher's school."
        ),

        responses={
            200: (
                TeacherStudentsResponseSerializer
            ),

            403: (
                ErrorResponseSerializer
            ),
        },
    )
    def get(
        self,
        request,
    ):

        teacher = get_teacher_for_user(
            request.user
        )

        if teacher is None:

            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "the student list."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        students = get_teacher_students(
            teacher
        )

        data = [
            build_student_summary(
                student
            )
            for student
            in students
        ]

        return Response(
            {
                "count": len(data),
                "students": data,
            },
            status=(
                status.HTTP_200_OK
            ),
        )


# ============================================================
# INDIVIDUAL STUDENT PROGRESS
# ============================================================

class TeacherStudentProgressView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Teacher"
        ],

        summary=(
            "Get student progress"
        ),

        description=(
            "Return complete progress information "
            "for a student belonging to the "
            "teacher's school."
        ),

        responses={
            200: (
                TeacherStudentProgressResponseSerializer
            ),

            403: (
                ErrorResponseSerializer
            ),

            404: (
                ErrorResponseSerializer
            ),
        },
    )
    def get(
        self,
        request,
        student_id,
    ):

        teacher = get_teacher_for_user(
            request.user
        )

        if teacher is None:

            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "student progress."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        student = get_teacher_student(
            teacher,
            student_id,
        )

        if student is None:

            return Response(
                {
                    "error": (
                        "Student not found in "
                        "your school."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return Response(
            build_teacher_student_progress(
                student
            ),
            status=(
                status.HTTP_200_OK
            ),
        )


# ============================================================
# WEAK TOPIC ANALYTICS
# ============================================================

class TeacherWeakTopicsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Teacher"
        ],

        summary=(
            "Get weak topic analytics"
        ),

        description=(
            "Identify weak and developing topics "
            "across students belonging to the "
            "teacher's school."
        ),

        responses={
            200: (
                TeacherWeakTopicsResponseSerializer
            ),

            403: (
                ErrorResponseSerializer
            ),
        },
    )
    def get(
        self,
        request,
    ):

        teacher = get_teacher_for_user(
            request.user
        )

        if teacher is None:

            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "weak-topic analytics."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        return Response(
            build_teacher_weak_topics(
                teacher
            ),
            status=(
                status.HTTP_200_OK
            ),
        )


# ============================================================
# RECENT QUIZ ATTEMPTS
# ============================================================

class TeacherRecentAttemptsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Teacher"
        ],

        summary=(
            "Get recent student attempts"
        ),

        description=(
            "Return recent quiz attempts from "
            "students in the teacher's school."
        ),

        parameters=[
            OpenApiParameter(
                name="limit",

                type=(
                    OpenApiTypes.INT
                ),

                location=(
                    OpenApiParameter.QUERY
                ),

                required=False,

                description=(
                    "Maximum number of attempts "
                    "to return. Minimum 1 and "
                    "maximum 100."
                ),
            ),
        ],

        responses={
            200: (
                TeacherRecentAttemptsResponseSerializer
            ),

            403: (
                ErrorResponseSerializer
            ),
        },
    )
    def get(
        self,
        request,
    ):

        teacher = get_teacher_for_user(
            request.user
        )

        if teacher is None:

            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "recent attempts."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        try:

            limit = int(
                request.query_params.get(
                    "limit",
                    20,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            limit = 20

        limit = max(
            1,
            min(
                limit,
                100,
            ),
        )

        return Response(
            build_teacher_recent_attempts(
                teacher,
                limit=limit,
            ),
            status=(
                status.HTTP_200_OK
            ),
        )