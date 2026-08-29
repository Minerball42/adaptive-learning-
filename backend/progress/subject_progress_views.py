from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Student

from .subject_progress import (
    build_subject_progress,
)

from .serializers import (
    ProgressErrorResponseSerializer,
    SubjectProgressResponseSerializer,
)


class MySubjectProgressView(APIView):
    """
    Return subject-level progress for the
    authenticated student.

    GET /api/progress/subject-progress/
    """

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Progress"
        ],

        summary=(
            "Get subject progress"
        ),

        description=(
            "Return subject-level completion and "
            "mastery information for the "
            "authenticated student's allowed "
            "subjects."
        ),

        responses={
            200: (
                SubjectProgressResponseSerializer
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

            student = (
                request.user.student
            )

        except Student.DoesNotExist:

            return Response(
                {
                    "error": (
                        "Only students can access "
                        "subject progress."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        if not student.grade_id:

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

        data = (
            build_subject_progress(
                student
            )
        )

        return Response(
            data,
            status=(
                status.HTTP_200_OK
            ),
        )