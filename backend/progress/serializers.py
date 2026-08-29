from rest_framework import serializers


# ============================================================
# COMMON ERROR
# ============================================================

class ProgressErrorResponseSerializer(
    serializers.Serializer
):
    error = serializers.CharField()


# ============================================================
# NORMAL QUIZ SUBMISSION
# ============================================================

class SubmitQuizAnswerSerializer(
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


class SubmitQuizRequestSerializer(
    serializers.Serializer
):
    quiz = serializers.IntegerField(
        min_value=1
    )

    answers = SubmitQuizAnswerSerializer(
        many=True
    )


class SubmitQuizResponseSerializer(
    serializers.Serializer
):
    message = serializers.CharField()

    attempt_id = serializers.IntegerField()


# ============================================================
# QUIZ ATTEMPT RESULTS
# ============================================================

class QuizAttemptAnswerResultSerializer(
    serializers.Serializer
):
    question = serializers.IntegerField()

    question_text = serializers.CharField()

    student_answer = serializers.CharField()

    correct_answer = serializers.CharField()

    correct = serializers.BooleanField()


class QuizAttemptResultSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()

    student = serializers.CharField()

    quiz = serializers.CharField()

    topic = serializers.CharField()

    score = serializers.IntegerField()

    total_questions = serializers.IntegerField()

    percentage = serializers.FloatField()

    attempted_at = serializers.DateTimeField()

    synced = serializers.BooleanField()

    answers = QuizAttemptAnswerResultSerializer(
        many=True
    )


# ============================================================
# TEACHER TOPIC PERFORMANCE
# ============================================================

class TopicPerformanceStudentSerializer(
    serializers.Serializer
):
    student_id = serializers.IntegerField()

    student_username = serializers.CharField()

    correct = serializers.IntegerField()

    total = serializers.IntegerField()

    attempt_count = serializers.IntegerField()

    percentage = serializers.FloatField()


class TopicPerformanceSerializer(
    serializers.Serializer
):
    topic_id = serializers.IntegerField()

    topic_name = serializers.CharField()

    students = TopicPerformanceStudentSerializer(
        many=True
    )


# ============================================================
# LEARNING PATH
# ============================================================

class PreviousTopicSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()

    name = serializers.CharField()

    level = serializers.CharField()

    mastery_score = serializers.FloatField()


class LearningPathTopicSerializer(
    serializers.Serializer
):
    topic_id = serializers.IntegerField()

    topic_name = serializers.CharField()

    chapter_id = serializers.IntegerField()

    chapter_name = serializers.CharField()

    subject_id = serializers.IntegerField()

    subject_name = serializers.CharField()

    status = serializers.CharField()

    unlocked = serializers.BooleanField()

    level = serializers.CharField()

    mastery_score = serializers.FloatField()

    percentage = serializers.FloatField()

    previous_topic = PreviousTopicSerializer(
        allow_null=True
    )


class LearningPathSummarySerializer(
    serializers.Serializer
):
    total_topics = serializers.IntegerField()

    completed = serializers.IntegerField()

    available = serializers.IntegerField()

    locked = serializers.IntegerField()

    completion_percentage = serializers.FloatField()


class LearningPathResponseSerializer(
    serializers.Serializer
):
    summary = LearningPathSummarySerializer()

    topics = LearningPathTopicSerializer(
        many=True
    )


# ============================================================
# CHAPTER PROGRESS
# ============================================================

class ChapterProgressTopicSerializer(
    serializers.Serializer
):
    topic_id = serializers.IntegerField()

    topic_name = serializers.CharField()

    level = serializers.CharField()

    mastery_score = serializers.FloatField()

    percentage = serializers.FloatField()

    attempt_count = serializers.IntegerField()


class ChapterProgressItemSerializer(
    serializers.Serializer
):
    chapter_id = serializers.IntegerField()

    chapter_number = serializers.IntegerField()

    chapter_name = serializers.CharField()

    subject_id = serializers.IntegerField()

    subject_name = serializers.CharField()

    status = serializers.CharField()

    total_topics = serializers.IntegerField()

    started_topics = serializers.IntegerField()

    completed_topics = serializers.IntegerField()

    remaining_topics = serializers.IntegerField()

    completion_percentage = serializers.FloatField()

    average_mastery = serializers.FloatField()

    topics = ChapterProgressTopicSerializer(
        many=True
    )


class ChapterProgressSummarySerializer(
    serializers.Serializer
):
    total_chapters = serializers.IntegerField()

    completed_chapters = serializers.IntegerField()

    in_progress_chapters = serializers.IntegerField()

    not_started_chapters = serializers.IntegerField()

    overall_completion_percentage = (
        serializers.FloatField()
    )


class ChapterProgressResponseSerializer(
    serializers.Serializer
):
    summary = ChapterProgressSummarySerializer()

    chapters = ChapterProgressItemSerializer(
        many=True
    )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

class DashboardStudentSerializer(
    serializers.Serializer
):
    username = serializers.CharField()

    email = serializers.EmailField(
        allow_blank=True
    )

    grade = serializers.CharField(
        allow_null=True
    )

    school = serializers.CharField(
        allow_blank=True
    )

    preferred_language = serializers.CharField()


class DashboardOverviewSerializer(
    serializers.Serializer
):
    total_topics = serializers.IntegerField()

    completed_topics = serializers.IntegerField()

    available_topics = serializers.IntegerField()

    locked_topics = serializers.IntegerField()

    topic_completion_percentage = (
        serializers.FloatField()
    )

    total_chapters = serializers.IntegerField()

    completed_chapters = serializers.IntegerField()

    in_progress_chapters = serializers.IntegerField()

    chapter_completion_percentage = (
        serializers.FloatField()
    )


class ContinueLearningSerializer(
    serializers.Serializer
):
    topic_id = serializers.IntegerField()

    topic_name = serializers.CharField()

    chapter_id = serializers.IntegerField()

    chapter_name = serializers.CharField()

    subject_id = serializers.IntegerField()

    subject_name = serializers.CharField()

    level = serializers.CharField()

    mastery_score = serializers.FloatField()

    status = serializers.CharField()

    action = serializers.CharField()


class RecentActivitySerializer(
    serializers.Serializer
):
    attempt_id = serializers.IntegerField()

    quiz_id = serializers.IntegerField()

    quiz_title = serializers.CharField()

    topic_id = serializers.IntegerField()

    topic_name = serializers.CharField()

    chapter_id = serializers.IntegerField()

    chapter_name = serializers.CharField()

    subject_id = serializers.IntegerField()

    subject_name = serializers.CharField()

    score = serializers.IntegerField()

    total_questions = serializers.IntegerField()

    percentage = serializers.FloatField()

    attempted_at = serializers.DateTimeField()


class DashboardResponseSerializer(
    serializers.Serializer
):
    student = DashboardStudentSerializer()

    status = serializers.CharField()

    overview = DashboardOverviewSerializer()

    continue_learning = ContinueLearningSerializer(
        allow_null=True
    )

    recommendations = serializers.ListField(
        child=serializers.DictField()
    )

    chapters = ChapterProgressItemSerializer(
        many=True
    )

    recent_activity = RecentActivitySerializer(
        many=True
    )
# ============================================================
# SUBJECT PROGRESS
# ============================================================


class SubjectProgressItemSerializer(
    serializers.Serializer
):
    subject_id = serializers.IntegerField()

    subject_name = serializers.CharField()

    subject_type = serializers.CharField()

    subject_type_display = serializers.CharField()

    language = serializers.CharField()

    status = serializers.CharField()

    total_chapters = serializers.IntegerField()

    total_topics = serializers.IntegerField()

    started_topics = serializers.IntegerField()

    completed_topics = serializers.IntegerField()

    remaining_topics = serializers.IntegerField()

    completion_percentage = serializers.FloatField()

    average_mastery = serializers.FloatField()


class SubjectProgressSummarySerializer(
    serializers.Serializer
):
    total_subjects = serializers.IntegerField()

    completed_subjects = serializers.IntegerField()

    in_progress_subjects = serializers.IntegerField()

    not_started_subjects = serializers.IntegerField()


class SubjectProgressResponseSerializer(
    serializers.Serializer
):
    summary = SubjectProgressSummarySerializer()

    subjects = SubjectProgressItemSerializer(
        many=True
    )