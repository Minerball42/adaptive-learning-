from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Teacher

from .teacher_services import (
    build_student_summary,
    build_teacher_dashboard,
    build_teacher_recent_attempts,
    build_teacher_student_progress,
    build_teacher_weak_topics,
    get_teacher_student,
    get_teacher_students,
)


def get_teacher_for_user(user):
    try:
        return user.teacher
    except Teacher.DoesNotExist:
        return None


class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teacher = get_teacher_for_user(request.user)

        if teacher is None:
            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "the teacher dashboard."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            build_teacher_dashboard(teacher),
            status=status.HTTP_200_OK,
        )


class TeacherStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teacher = get_teacher_for_user(request.user)

        if teacher is None:
            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "the student list."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        students = get_teacher_students(teacher)

        data = [
            build_student_summary(student)
            for student in students
        ]

        return Response(
            {
                "count": len(data),
                "students": data,
            },
            status=status.HTTP_200_OK,
        )


class TeacherStudentProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        teacher = get_teacher_for_user(request.user)

        if teacher is None:
            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "student progress."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
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
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            build_teacher_student_progress(student),
            status=status.HTTP_200_OK,
        )


class TeacherWeakTopicsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teacher = get_teacher_for_user(request.user)

        if teacher is None:
            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "weak-topic analytics."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            build_teacher_weak_topics(teacher),
            status=status.HTTP_200_OK,
        )


class TeacherRecentAttemptsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teacher = get_teacher_for_user(request.user)

        if teacher is None:
            return Response(
                {
                    "error": (
                        "Only teachers can access "
                        "recent attempts."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            limit = int(
                request.query_params.get(
                    "limit",
                    20,
                )
            )
        except (TypeError, ValueError):
            limit = 20

        limit = max(1, min(limit, 100))

        return Response(
            build_teacher_recent_attempts(
                teacher,
                limit=limit,
            ),
            status=status.HTTP_200_OK,
        )