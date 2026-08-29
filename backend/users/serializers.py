from django.contrib.auth.models import User
from rest_framework import serializers

from courses.models import Subject

from .models import Student

# ============================================================
# STUDENT REGISTRATION
# ============================================================

class StudentRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        write_only=True
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Student

        fields = [
            "username",
            "password",
            "email",
            "school",
            "preferred_language",
        ]

    def create(
        self,
        validated_data,
    ):
        username = validated_data.pop(
            "username"
        )

        password = validated_data.pop(
            "password"
        )

        email = validated_data.pop(
            "email",
            "",
        )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        student = Student.objects.create(
            user=user,
            **validated_data,
        )

        return student

class StudentSelectedSubjectSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Subject

        fields = [
            "id",
            "name",
            "subject_type",
            "language",
            "is_optional",
            "display_order",
        ]
# ============================================================
# STUDENT PROFILE
# ============================================================

class StudentProfileSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    selected_subjects = (
        StudentSelectedSubjectSerializer(
            many=True,
            read_only=True,
        )
    )

    class Meta:
        model = Student

        fields = [
            "username",
            "email",
            "grade",
            "school",
            "preferred_language",
            "selected_subjects",
        ]
class StudentSubjectSelectionRequestSerializer(
    serializers.Serializer
):
    first_language = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    second_language = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    third_language = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    optional_subjects = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1
        ),
        required=False,
        default=list,
    )


class StudentAvailableSubjectsResponseSerializer(
    serializers.Serializer
):
    grade = serializers.DictField()

    core_subjects = StudentSelectedSubjectSerializer(
        many=True
    )

    first_languages = StudentSelectedSubjectSerializer(
        many=True
    )

    second_languages = StudentSelectedSubjectSerializer(
        many=True
    )

    third_languages = StudentSelectedSubjectSerializer(
        many=True
    )

    optional_subjects = StudentSelectedSubjectSerializer(
        many=True
    )

    selected_subjects = StudentSelectedSubjectSerializer(
        many=True
    )


class TeacherStudentProgressResponseSerializer(
    serializers.Serializer
):
    student = serializers.DictField()

    status = serializers.CharField()

    overview = serializers.DictField()

    subject_progress = serializers.ListField(
        child=serializers.DictField()
    )

    continue_learning = serializers.DictField(
        allow_null=True
    )

    recommendations = serializers.ListField(
        child=serializers.DictField()
    )

    chapters = serializers.ListField(
        child=serializers.DictField()
    )

    recent_activity = serializers.ListField(
        child=serializers.DictField()
    )
    message = serializers.CharField()

    selected_subjects = StudentSelectedSubjectSerializer(
        many=True
    )
class StudentAvailableSubjectsResponseSerializer(
    serializers.Serializer
):
    grade = serializers.DictField()

    core_subjects = (
        StudentSelectedSubjectSerializer(
            many=True
        )
    )

    first_languages = (
        StudentSelectedSubjectSerializer(
            many=True
        )
    )

    second_languages = (
        StudentSelectedSubjectSerializer(
            many=True
        )
    )

    third_languages = (
        StudentSelectedSubjectSerializer(
            many=True
        )
    )

    optional_subjects = (
        StudentSelectedSubjectSerializer(
            many=True
        )
    )

    selected_subjects = (
        StudentSelectedSubjectSerializer(
            many=True
        )
    )


class StudentSubjectSelectionResponseSerializer(
    serializers.Serializer
):
    message = serializers.CharField()

    selected_subjects = (
        StudentSelectedSubjectSerializer(
            many=True
        )
    )
# ============================================================
# SWAGGER / API DOCUMENTATION SERIALIZERS
# ============================================================

class LoginRequestSerializer(
    serializers.Serializer
):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )


class ErrorResponseSerializer(
    serializers.Serializer
):

    error = serializers.CharField()


class MessageResponseSerializer(
    serializers.Serializer
):

    message = serializers.CharField()


class StudentRegisterResponseSerializer(
    serializers.Serializer
):

    message = serializers.CharField()

    token = serializers.CharField()

    student = StudentProfileSerializer()


class StudentLoginResponseSerializer(
    serializers.Serializer
):

    message = serializers.CharField()

    token = serializers.CharField()

    student = StudentProfileSerializer()


class TeacherProfileSerializer(
    serializers.Serializer
):

    username = serializers.CharField()

    email = serializers.EmailField(
        allow_blank=True
    )

    school = serializers.CharField()


class TeacherLoginResponseSerializer(
    serializers.Serializer
):

    message = serializers.CharField()

    token = serializers.CharField()

    teacher = TeacherProfileSerializer()


class AssignStudentGradeRequestSerializer(
    serializers.Serializer
):

    grade = serializers.IntegerField(
        min_value=1
    )


class AssignStudentGradeResponseSerializer(
    serializers.Serializer
):

    message = serializers.CharField()

    student = StudentProfileSerializer()
# ============================================================
# TEACHER API DOCUMENTATION SERIALIZERS
# ============================================================


class TeacherDashboardTeacherSerializer(
    serializers.Serializer
):
    teacher_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField(
        allow_blank=True
    )
    school = serializers.CharField()


class TeacherStudentSummarySerializer(
    serializers.Serializer
):
    student_id = serializers.IntegerField()
    username = serializers.CharField()

    email = serializers.EmailField(
        allow_blank=True
    )

    grade = serializers.CharField(
        allow_null=True
    )

    school = serializers.CharField()

    preferred_language = (
        serializers.CharField()
    )

    total_topics = serializers.IntegerField()

    completed_topics = (
        serializers.IntegerField()
    )

    available_topics = (
        serializers.IntegerField()
    )

    locked_topics = serializers.IntegerField()

    completion_percentage = (
        serializers.FloatField()
    )

    quiz_attempts = serializers.IntegerField()

    quiz_accuracy = serializers.FloatField()


class TeacherDashboardOverviewSerializer(
    serializers.Serializer
):
    total_students = serializers.IntegerField()

    active_students = serializers.IntegerField()

    completed_students = (
        serializers.IntegerField()
    )

    students_needing_help = (
        serializers.IntegerField()
    )

    total_quiz_attempts = (
        serializers.IntegerField()
    )

    average_completion_percentage = (
        serializers.FloatField()
    )

    average_quiz_accuracy = (
        serializers.FloatField()
    )


class TeacherDashboardResponseSerializer(
    serializers.Serializer
):
    teacher = TeacherDashboardTeacherSerializer()

    overview = (
        TeacherDashboardOverviewSerializer()
    )

    students = TeacherStudentSummarySerializer(
        many=True
    )


class TeacherStudentsResponseSerializer(
    serializers.Serializer
):
    count = serializers.IntegerField()

    students = TeacherStudentSummarySerializer(
        many=True
    )


class TeacherStudentProgressResponseSerializer(
    serializers.Serializer
):
    student = serializers.DictField()

    status = serializers.CharField()

    overview = serializers.DictField()

    continue_learning = serializers.DictField(
        allow_null=True
    )

    recommendations = serializers.ListField(
        child=serializers.DictField()
    )

    chapters = serializers.ListField(
        child=serializers.DictField()
    )

    recent_activity = serializers.ListField(
        child=serializers.DictField()
    )


class WeakTopicStudentSerializer(
    serializers.Serializer
):
    student_id = serializers.IntegerField()
    username = serializers.CharField()
    level = serializers.CharField()

    mastery_score = serializers.FloatField()

    attempt_count = serializers.IntegerField()


class WeakTopicSerializer(
    serializers.Serializer
):
    topic_id = serializers.IntegerField()
    topic_name = serializers.CharField()

    chapter_id = serializers.IntegerField()
    chapter_name = serializers.CharField()

    subject_id = serializers.IntegerField()
    subject_name = serializers.CharField()

    weak_students = serializers.IntegerField()

    developing_students = (
        serializers.IntegerField()
    )

    student_count = serializers.IntegerField()

    attempt_count = serializers.IntegerField()

    average_mastery = serializers.FloatField()

    students = WeakTopicStudentSerializer(
        many=True
    )


class TeacherWeakTopicsResponseSerializer(
    serializers.Serializer
):
    count = serializers.IntegerField()

    weak_topics = WeakTopicSerializer(
        many=True
    )


class TeacherRecentAttemptSerializer(
    serializers.Serializer
):
    attempt_id = serializers.IntegerField()

    student_id = serializers.IntegerField()

    username = serializers.CharField()

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


class TeacherRecentAttemptsResponseSerializer(
    serializers.Serializer
):
    count = serializers.IntegerField()

    attempts = TeacherRecentAttemptSerializer(
        many=True
    )