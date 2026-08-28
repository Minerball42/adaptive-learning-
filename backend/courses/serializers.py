from rest_framework import serializers

from .models import (
    Board,
    AcademicYear,
    Grade,
    Subject,
    Chapter,
    Topic,
    Note,
    LearningContent,
)


# ============================================================
# BOARD
# ============================================================


class BoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board

        fields = [
            "id",
            "code",
            "name",
            "state",
            "country",
            "is_active",
        ]


# ============================================================
# ACADEMIC YEAR
# ============================================================


class AcademicYearSerializer(
    serializers.ModelSerializer
):

    board_code = serializers.CharField(
        source="board.code",
        read_only=True,
    )

    board_name = serializers.CharField(
        source="board.name",
        read_only=True,
    )

    class Meta:
        model = AcademicYear

        fields = [
            "id",
            "board",
            "board_code",
            "board_name",
            "name",
            "is_active",
        ]


# ============================================================
# GRADE
# ============================================================


class GradeSerializer(serializers.ModelSerializer):

    academic_year_name = (
        serializers.SerializerMethodField()
    )

    board_code = (
        serializers.SerializerMethodField()
    )

    board_name = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Grade

        fields = [
            "id",
            "academic_year",
            "academic_year_name",
            "board_code",
            "board_name",
            "name",
            "level",
            "description",
        ]

    def get_academic_year_name(
        self,
        obj,
    ):
        if obj.academic_year:
            return obj.academic_year.name

        return None

    def get_board_code(
        self,
        obj,
    ):
        if (
            obj.academic_year
            and obj.academic_year.board
        ):
            return (
                obj.academic_year.board.code
            )

        return None

    def get_board_name(
        self,
        obj,
    ):
        if (
            obj.academic_year
            and obj.academic_year.board
        ):
            return (
                obj.academic_year.board.name
            )

        return None


# ============================================================
# SUBJECT
# ============================================================


class SubjectSerializer(
    serializers.ModelSerializer
):

    grade_name = (
        serializers.SerializerMethodField()
    )

    subject_type_display = (
        serializers.CharField(
            source="get_subject_type_display",
            read_only=True,
        )
    )

    class Meta:
        model = Subject

        fields = [
            "id",
            "grade",
            "grade_name",
            "name",
            "description",
            "language",
            "subject_type",
            "subject_type_display",
            "is_optional",
            "display_order",
        ]

    def get_grade_name(
        self,
        obj,
    ):
        if obj.grade:
            return obj.grade.name

        return None


# ============================================================
# CHAPTER
# ============================================================


class ChapterSerializer(
    serializers.ModelSerializer
):

    subject_name = serializers.CharField(
        source="subject.name",
        read_only=True,
    )

    subject_type = serializers.CharField(
        source="subject.subject_type",
        read_only=True,
    )

    subject_language = (
        serializers.CharField(
            source="subject.language",
            read_only=True,
        )
    )

    class Meta:
        model = Chapter

        fields = [
            "id",
            "subject",
            "subject_name",
            "subject_type",
            "subject_language",
            "chapter_number",
            "name",
            "description",
        ]


# ============================================================
# TOPIC
# ============================================================


class TopicSerializer(
    serializers.ModelSerializer
):

    chapter_name = serializers.CharField(
        source="chapter.name",
        read_only=True,
    )

    chapter_number = (
        serializers.IntegerField(
            source="chapter.chapter_number",
            read_only=True,
        )
    )

    subject_id = serializers.IntegerField(
        source="chapter.subject_id",
        read_only=True,
    )

    subject_name = serializers.CharField(
        source="chapter.subject.name",
        read_only=True,
    )

    subject_type = serializers.CharField(
        source="chapter.subject.subject_type",
        read_only=True,
    )

    subject_language = (
        serializers.CharField(
            source="chapter.subject.language",
            read_only=True,
        )
    )

    has_learning_content = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Topic

        fields = [
            "id",
            "chapter",
            "chapter_name",
            "chapter_number",
            "subject_id",
            "subject_name",
            "subject_type",
            "subject_language",
            "name",
            "description",
            "difficulty",
            "has_learning_content",
        ]

    def get_has_learning_content(
        self,
        obj,
    ):
        try:
            obj.learning_content
            return True

        except LearningContent.DoesNotExist:
            return False


# ============================================================
# LEARNING CONTENT
# ============================================================


class LearningContentSerializer(
    serializers.ModelSerializer
):

    topic_name = serializers.CharField(
        source="topic.name",
        read_only=True,
    )

    topic_difficulty = (
        serializers.IntegerField(
            source="topic.difficulty",
            read_only=True,
        )
    )

    chapter_id = serializers.IntegerField(
        source="topic.chapter_id",
        read_only=True,
    )

    chapter_name = serializers.CharField(
        source="topic.chapter.name",
        read_only=True,
    )

    chapter_number = (
        serializers.IntegerField(
            source=(
                "topic.chapter.chapter_number"
            ),
            read_only=True,
        )
    )

    subject_id = serializers.IntegerField(
        source=(
            "topic.chapter.subject_id"
        ),
        read_only=True,
    )

    subject_name = serializers.CharField(
        source=(
            "topic.chapter.subject.name"
        ),
        read_only=True,
    )

    subject_type = serializers.CharField(
        source=(
            "topic.chapter.subject.subject_type"
        ),
        read_only=True,
    )

    subject_language = (
        serializers.CharField(
            source=(
                "topic.chapter.subject.language"
            ),
            read_only=True,
        )
    )

    class Meta:
        model = LearningContent

        fields = [
            "id",

            "subject_id",
            "subject_name",
            "subject_type",
            "subject_language",

            "chapter_id",
            "chapter_number",
            "chapter_name",

            "topic",
            "topic_name",
            "topic_difficulty",

            "explanation",
            "key_concepts",
            "easy_method",
            "worked_example",
            "common_mistakes",

            "created_at",
            "updated_at",
        ]


# ============================================================
# NOTES
# ============================================================


class NoteSerializer(
    serializers.ModelSerializer
):

    chapter_name = serializers.CharField(
        source="chapter.name",
        read_only=True,
    )

    chapter_number = (
        serializers.IntegerField(
            source="chapter.chapter_number",
            read_only=True,
        )
    )

    subject_id = serializers.IntegerField(
        source="chapter.subject_id",
        read_only=True,
    )

    subject_name = serializers.CharField(
        source="chapter.subject.name",
        read_only=True,
    )

    subject_type = serializers.CharField(
        source="chapter.subject.subject_type",
        read_only=True,
    )

    class Meta:
        model = Note

        fields = [
            "id",

            "chapter",
            "chapter_name",
            "chapter_number",

            "subject_id",
            "subject_name",
            "subject_type",

            "title",
            "description",
            "pdf_file",
            "uploaded_at",
        ]