from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Student

from .chapter_progress import (
    build_chapter_progress,
)

from .serializers import (
    ChapterProgressResponseSerializer,
    ProgressErrorResponseSerializer,
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

    @extend_schema(
        tags=[
            "Progress"
        ],

        summary=(
            "Get chapter progress"
        ),

        description=(
            "Return chapter-level completion, "
            "mastery and topic progress for "
            "the authenticated student."
        ),

        responses={
            200: (
                ChapterProgressResponseSerializer
            ),

            400: (
                ProgressErrorResponseSerializer
            ),

            403: (
                ProgressErrorResponseSerializer
            ),
        },
    )
    def get(
        self,
        request,
    ):

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
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        if not student.grade:

            return Response(
                {
                    "error": (
                        "The student must have "
                        "a grade assigned."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        data = build_chapter_progress(
            student
        )

        return Response(
            data,
            status=(
                status.HTTP_200_OK
            ),
        )