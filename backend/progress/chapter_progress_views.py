from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Student

from .chapter_progress import (
    build_chapter_progress,
)


class MyChapterProgressView(APIView):
    """
    Return chapter-level progress for
    the authenticated student.

    GET /api/progress/chapter-progress/
    """

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        try:
            student = request.user.student

        except Student.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Only students can access "
                        "chapter progress."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not student.grade:
            return Response(
                {
                    "error": (
                        "The student must have "
                        "a grade assigned."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = build_chapter_progress(
            student
        )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )