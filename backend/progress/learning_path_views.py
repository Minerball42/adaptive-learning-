from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Student

from .learning_path import build_learning_path


class MyLearningPathView(APIView):
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
                        "the learning path."
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

        data = build_learning_path(
            student
        )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )