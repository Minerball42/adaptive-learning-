from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Student

from .dashboard import build_dashboard

from .serializers import (
    DashboardResponseSerializer,
    ProgressErrorResponseSerializer,
)


class MyDashboardView(APIView):
    """
    Student dashboard.

    GET /api/progress/dashboard/
    """

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Progress"
        ],

        summary=(
            "Get student dashboard"
        ),

        description=(
            "Return the authenticated student's "
            "dashboard including learning progress, "
            "chapter completion, recommendations, "
            "continue-learning information and "
            "recent quiz activity."
        ),

        responses={
            200: (
                DashboardResponseSerializer
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
                        "the student dashboard."
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

        data = build_dashboard(
            student
        )

        return Response(
            data,
            status=(
                status.HTTP_200_OK
            ),
        )