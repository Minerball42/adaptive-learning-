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


class BoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = "__all__"


class AcademicYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = AcademicYear
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grade
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = "__all__"


class ChapterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chapter
        fields = "__all__"


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = "__all__"


class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = "__all__"


class LearningContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = LearningContent
        fields = "__all__"