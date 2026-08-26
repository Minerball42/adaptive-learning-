from rest_framework import serializers

from quizzes.serializers import (
    AdaptiveMasterySerializer,
)


# ============================================================
# OFFLINE QUIZ ATTEMPT REQUEST
# ============================================================

class OfflineAnswerRequestSerializer(
    serializers.Serializer
):
    question = serializers.IntegerField(
        min_value=1
    )

    answer = serializers.ChoiceField(
        choices=[
            "A",
            "B",
            "C",
            "D",
        ]
    )


class OfflineQuizAttemptRequestSerializer(
    serializers.Serializer
):
    client_attempt_id = serializers.UUIDField()

    quiz_id = serializers.IntegerField(
        min_value=1
    )

    device_id = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
    )

    client_created_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    answers = OfflineAnswerRequestSerializer(
        many=True
    )


# ============================================================
# SINGLE SYNC RESPONSE
# ============================================================

class OfflineAttemptResultSerializer(
    serializers.Serializer
):
    attempt_id = serializers.IntegerField()

    quiz_id = serializers.IntegerField()

    topic_id = serializers.IntegerField()

    topic_name = serializers.CharField()

    score = serializers.IntegerField()

    total_questions = serializers.IntegerField()

    percentage = serializers.FloatField()


class OfflineSyncSuccessResponseSerializer(
    serializers.Serializer
):
    sync_id = serializers.UUIDField()

    client_attempt_id = serializers.UUIDField()

    status = serializers.CharField()

    already_synced = serializers.BooleanField()

    device_id = serializers.CharField(
        allow_blank=True
    )

    received_at = serializers.DateTimeField()

    synced_at = serializers.DateTimeField(
        allow_null=True
    )

    attempt = OfflineAttemptResultSerializer()

    mastery = AdaptiveMasterySerializer()


# ============================================================
# ERROR / FAILED SYNC RESPONSE
# ============================================================

class OfflineSyncErrorResponseSerializer(
    serializers.Serializer
):
    error = serializers.CharField()

    sync_id = serializers.UUIDField(
        required=False
    )

    status = serializers.CharField(
        required=False
    )


# ============================================================
# BATCH REQUEST
# ============================================================

class OfflineBatchSyncRequestSerializer(
    serializers.Serializer
):
    attempts = OfflineQuizAttemptRequestSerializer(
        many=True
    )


# ============================================================
# BATCH RESPONSE
# ============================================================

class OfflineBatchSummarySerializer(
    serializers.Serializer
):
    total = serializers.IntegerField()

    synced = serializers.IntegerField()

    already_synced = serializers.IntegerField()

    failed = serializers.IntegerField()


class OfflineBatchResultSerializer(
    serializers.Serializer
):
    index = serializers.IntegerField()

    status_code = serializers.IntegerField()

    sync_id = serializers.UUIDField(
        required=False
    )

    client_attempt_id = serializers.UUIDField(
        required=False
    )

    status = serializers.CharField(
        required=False
    )

    already_synced = serializers.BooleanField(
        required=False
    )

    device_id = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    received_at = serializers.DateTimeField(
        required=False
    )

    synced_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    attempt = OfflineAttemptResultSerializer(
        required=False
    )

    mastery = AdaptiveMasterySerializer(
        required=False
    )

    error = serializers.CharField(
        required=False
    )


class OfflineBatchSyncResponseSerializer(
    serializers.Serializer
):
    summary = OfflineBatchSummarySerializer()

    results = OfflineBatchResultSerializer(
        many=True
    )


# ============================================================
# SYNC STATUS RESPONSE
# ============================================================

class OfflineStatusSummarySerializer(
    serializers.Serializer
):
    total = serializers.IntegerField()

    pending = serializers.IntegerField()

    synced = serializers.IntegerField()

    failed = serializers.IntegerField()


class OfflineStatusRecordSerializer(
    serializers.Serializer
):
    sync_id = serializers.UUIDField()

    client_attempt_id = serializers.UUIDField()

    device_id = serializers.CharField(
        allow_blank=True
    )

    status = serializers.CharField()

    client_created_at = serializers.DateTimeField(
        allow_null=True
    )

    received_at = serializers.DateTimeField()

    synced_at = serializers.DateTimeField(
        allow_null=True
    )

    error_message = serializers.CharField(
        allow_blank=True
    )

    attempt_id = serializers.IntegerField(
        allow_null=True
    )

    quiz_id = serializers.IntegerField(
        allow_null=True
    )

    topic_id = serializers.IntegerField(
        allow_null=True
    )

    topic_name = serializers.CharField(
        allow_null=True
    )


class OfflineSyncStatusResponseSerializer(
    serializers.Serializer
):
    summary = OfflineStatusSummarySerializer()

    records = OfflineStatusRecordSerializer(
        many=True
    )