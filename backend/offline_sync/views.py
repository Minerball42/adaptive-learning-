from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Student

from .models import OfflineSyncRecord
from .services import sync_offline_quiz_attempt


def get_student_for_user(user):
    """
    Return the Student profile for the
    authenticated user.
    """

    try:
        return user.student

    except Student.DoesNotExist:
        return None


class OfflineQuizAttemptSyncView(APIView):
    """
    Synchronize one offline quiz attempt.

    POST /api/sync/quiz-attempts/
    """

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        student = get_student_for_user(
            request.user
        )

        if student is None:
            return Response(
                {
                    "error": (
                        "Only students can "
                        "synchronize quiz attempts."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        data, response_status = (
            sync_offline_quiz_attempt(
                student=student,
                payload=request.data,
            )
        )

        return Response(
            data,
            status=response_status,
        )


class OfflineBatchSyncView(APIView):
    """
    Synchronize multiple offline quiz
    attempts in one request.

    POST /api/sync/batch/
    """

    permission_classes = [
        IsAuthenticated
    ]

    MAX_BATCH_SIZE = 50

    def post(self, request):

        student = get_student_for_user(
            request.user
        )

        if student is None:
            return Response(
                {
                    "error": (
                        "Only students can "
                        "synchronize quiz attempts."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        attempts = request.data.get(
            "attempts"
        )

        if not isinstance(
            attempts,
            list,
        ):
            return Response(
                {
                    "error": (
                        "attempts must be a list."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(attempts) == 0:
            return Response(
                {
                    "error": (
                        "At least one attempt "
                        "is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            len(attempts)
            >
            self.MAX_BATCH_SIZE
        ):
            return Response(
                {
                    "error": (
                        "A maximum of 50 attempts "
                        "can be synchronized "
                        "in one request."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []

        synced_count = 0
        already_synced_count = 0
        failed_count = 0

        for index, attempt_payload in enumerate(
            attempts
        ):

            if not isinstance(
                attempt_payload,
                dict,
            ):
                failed_count += 1

                results.append(
                    {
                        "index": index,
                        "status": "failed",
                        "status_code": 400,
                        "error": (
                            "Each attempt must "
                            "be an object."
                        ),
                    }
                )

                continue

            data, response_status = (
                sync_offline_quiz_attempt(
                    student=student,
                    payload=attempt_payload,
                )
            )

            result = {
                "index": index,
                "status_code": response_status,
                **data,
            }

            results.append(
                result
            )

            if (
                response_status
                in (200, 201)
                and
                data.get("status")
                == "synced"
            ):

                synced_count += 1

                if data.get(
                    "already_synced",
                    False,
                ):
                    already_synced_count += 1

            else:
                failed_count += 1

        return Response(
            {
                "summary": {
                    "total": len(attempts),

                    "synced": (
                        synced_count
                    ),

                    "already_synced": (
                        already_synced_count
                    ),

                    "failed": (
                        failed_count
                    ),
                },

                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class OfflineSyncStatusView(APIView):
    """
    Return synchronization status for
    the authenticated student.

    GET /api/sync/status/
    """

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        student = get_student_for_user(
            request.user
        )

        if student is None:
            return Response(
                {
                    "error": (
                        "Only students can "
                        "access sync status."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        records = (
            OfflineSyncRecord.objects
            .filter(
                student=student
            )
            .select_related(
                "quiz_attempt",
                "quiz_attempt__quiz",
                "quiz_attempt__quiz__topic",
            )
            .order_by(
                "-received_at"
            )
        )

        total = records.count()

        pending = records.filter(
            status="pending"
        ).count()

        synced = records.filter(
            status="synced"
        ).count()

        failed = records.filter(
            status="failed"
        ).count()

        record_data = []

        for record in records[:50]:

            attempt = (
                record.quiz_attempt
            )

            item = {
                "sync_id": str(
                    record.id
                ),

                "client_attempt_id": str(
                    record.client_attempt_id
                ),

                "device_id": (
                    record.device_id
                ),

                "status": (
                    record.status
                ),

                "client_created_at": (
                    record.client_created_at
                ),

                "received_at": (
                    record.received_at
                ),

                "synced_at": (
                    record.synced_at
                ),

                "error_message": (
                    record.error_message
                ),

                "attempt_id": None,

                "quiz_id": None,

                "topic_id": None,

                "topic_name": None,
            }

            if attempt:

                item[
                    "attempt_id"
                ] = attempt.id

                item[
                    "quiz_id"
                ] = attempt.quiz.id

                item[
                    "topic_id"
                ] = (
                    attempt.quiz.topic.id
                )

                item[
                    "topic_name"
                ] = (
                    attempt.quiz.topic.name
                )

            record_data.append(
                item
            )

        return Response(
            {
                "summary": {
                    "total": total,
                    "pending": pending,
                    "synced": synced,
                    "failed": failed,
                },

                "records": (
                    record_data
                ),
            },
            status=status.HTTP_200_OK,
        )