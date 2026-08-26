from rest_framework import serializers

from .models import (
    Quiz,
    Question,
)


# ============================================================
# DATABASE MODEL SERIALIZERS
# ============================================================

class QuizSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quiz
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    """
    Student-facing question serializer.

    correct_answer is intentionally excluded.
    """

    class Meta:
        model = Question

        fields = [
            "id",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "difficulty",
            "quiz",
        ]


# ============================================================
# SWAGGER - COMMON ERROR
# ============================================================

class QuizErrorResponseSerializer(
    serializers.Serializer
):
    error = serializers.CharField()


# ============================================================
# MASTERY SERIALIZERS
# ============================================================

class AdaptiveDifficultyStatsSerializer(
    serializers.Serializer
):
    correct = serializers.IntegerField()
    total = serializers.IntegerField()
    percentage = serializers.FloatField()


class AdaptiveDifficultyPerformanceSerializer(
    serializers.Serializer
):
    easy = AdaptiveDifficultyStatsSerializer()
    medium = AdaptiveDifficultyStatsSerializer()
    hard = AdaptiveDifficultyStatsSerializer()


class AdaptiveMasterySerializer(
    serializers.Serializer
):
    correct = serializers.IntegerField()

    total = serializers.IntegerField()

    attempt_count = serializers.IntegerField()

    percentage = serializers.FloatField()

    recent_percentage = serializers.FloatField()

    mastery_score = serializers.FloatField()

    level = serializers.CharField()

    difficulty_performance = (
        AdaptiveDifficultyPerformanceSerializer()
    )


# ============================================================
# ADAPTIVE QUIZ GET RESPONSE
# ============================================================

class AdaptiveQuizSessionSerializer(
    serializers.Serializer
):
    id = serializers.UUIDField()

    status = serializers.CharField()

    created_at = serializers.DateTimeField()

    expires_at = serializers.DateTimeField()


class AdaptiveQuizTopicSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()

    name = serializers.CharField()

    chapter = serializers.CharField()

    subject = serializers.CharField()


class AdaptiveSelectionSerializer(
    serializers.Serializer
):
    difficulty_value = serializers.IntegerField()

    difficulty = serializers.CharField()

    question_limit = serializers.IntegerField()

    fallback_used = serializers.BooleanField()

    actual_difficulties = serializers.ListField(
        child=serializers.IntegerField()
    )


class AdaptiveQuizInfoSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()

    title = serializers.CharField()

    description = serializers.CharField(
        allow_blank=True
    )


class AdaptiveQuizResponseSerializer(
    serializers.Serializer
):
    session = AdaptiveQuizSessionSerializer()

    topic = AdaptiveQuizTopicSerializer()

    mastery = AdaptiveMasterySerializer()

    adaptive_selection = (
        AdaptiveSelectionSerializer()
    )

    quiz = AdaptiveQuizInfoSerializer()

    questions = QuestionSerializer(
        many=True
    )


# ============================================================
# ADAPTIVE QUIZ SUBMISSION REQUEST
# ============================================================

class AdaptiveAnswerRequestSerializer(
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


class AdaptiveQuizSubmitRequestSerializer(
    serializers.Serializer
):
    session_id = serializers.UUIDField()

    answers = AdaptiveAnswerRequestSerializer(
        many=True
    )


# ============================================================
# ADAPTIVE QUIZ SUBMISSION RESPONSE
# ============================================================

class AdaptiveSubmittedSessionSerializer(
    serializers.Serializer
):
    id = serializers.UUIDField()

    status = serializers.CharField()

    submitted_at = serializers.DateTimeField()


class AdaptiveSubmitTopicSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()

    name = serializers.CharField()


class AdaptiveSubmitQuizSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()

    title = serializers.CharField()


class AdaptiveAttemptResultSerializer(
    serializers.Serializer
):
    score = serializers.IntegerField()

    total_questions = serializers.IntegerField()

    percentage = serializers.FloatField()


class AdaptiveNextDifficultySerializer(
    serializers.Serializer
):
    value = serializers.IntegerField()

    name = serializers.CharField()


class AdaptiveQuizSubmitResponseSerializer(
    serializers.Serializer
):
    message = serializers.CharField()

    session = (
        AdaptiveSubmittedSessionSerializer()
    )

    attempt_id = serializers.IntegerField()

    topic = AdaptiveSubmitTopicSerializer()

    quiz = AdaptiveSubmitQuizSerializer()

    attempt = AdaptiveAttemptResultSerializer()

    mastery_before = AdaptiveMasterySerializer()

    mastery_after = AdaptiveMasterySerializer()

    next_adaptive_difficulty = (
        AdaptiveNextDifficultySerializer()
    )