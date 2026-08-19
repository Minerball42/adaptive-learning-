
from rest_framework import viewsets
from .models import (
    Grade,
    Subject,
    Chapter,
    Topic,
    Note,
    LearningContent,
)
from users.models import Student
from .serializers import (
    GradeSerializer,
    SubjectSerializer,
    ChapterSerializer,
    TopicSerializer,
    NoteSerializer,
    LearningContentSerializer,
)


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        queryset = Subject.objects.all()

        if self.request.user.is_authenticated:
            try:
                student = self.request.user.student

                if student.grade:
                    return queryset.filter(grade=student.grade)

                return queryset.none()

            except Exception:
                pass

        return queryset


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChapterSerializer

    def get_queryset(self):
        queryset = Chapter.objects.all()

        if self.request.user.is_authenticated:
            try:
                student = self.request.user.student

                if student.grade:
                    queryset = queryset.filter(
                        subject__grade=student.grade
                    )
                else:
                    return queryset.none()

            except Student.DoesNotExist:
                pass

        subject_id = self.request.query_params.get("subject")

        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        return queryset


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TopicSerializer

    def get_queryset(self):
        queryset = Topic.objects.all()

        if self.request.user.is_authenticated:
            try:
                student = self.request.user.student

                if student.grade:
                    queryset = queryset.filter(
                        chapter__subject__grade=student.grade
                    )
                else:
                    return queryset.none()

            except Student.DoesNotExist:
                pass

        chapter_id = self.request.query_params.get("chapter")

        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)

        return queryset


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer

    def get_queryset(self):
        queryset = Note.objects.all()

        chapter_id = self.request.query_params.get("chapter")

        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)

        return queryset

class LearningContentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LearningContentSerializer

    def get_queryset(self):
        queryset = LearningContent.objects.all()

        if self.request.user.is_authenticated:
            try:
                student = self.request.user.student

                if student.grade:
                    queryset = queryset.filter(
                        topic__chapter__subject__grade=student.grade
                    )
                else:
                    return queryset.none()

            except Student.DoesNotExist:
                return queryset.none()

        topic_id = self.request.query_params.get("topic")

        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)

        return queryset