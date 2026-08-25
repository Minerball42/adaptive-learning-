from rest_framework import viewsets

from users.models import Student

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

from .serializers import (
    BoardSerializer,
    AcademicYearSerializer,
    GradeSerializer,
    SubjectSerializer,
    ChapterSerializer,
    TopicSerializer,
    NoteSerializer,
    LearningContentSerializer,
)


class BoardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BoardSerializer
    queryset = Board.objects.filter(
        is_active=True
    )


class AcademicYearViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AcademicYearSerializer

    def get_queryset(self):
        queryset = AcademicYear.objects.select_related(
            "board"
        ).all()

        board_id = self.request.query_params.get(
            "board"
        )

        if board_id:
            queryset = queryset.filter(
                board_id=board_id
            )

        return queryset


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GradeSerializer

    def get_queryset(self):
        queryset = Grade.objects.select_related(
            "academic_year",
            "academic_year__board"
        ).all()

        academic_year_id = self.request.query_params.get(
            "academic_year"
        )

        if academic_year_id:
            queryset = queryset.filter(
                academic_year_id=academic_year_id
            )

        board_id = self.request.query_params.get(
            "board"
        )

        if board_id:
            queryset = queryset.filter(
                academic_year__board_id=board_id
            )

        return queryset


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        queryset = Subject.objects.select_related(
            "grade"
        ).all()

        if self.request.user.is_authenticated:

            try:
                student = self.request.user.student

                if student.grade:
                    return queryset.filter(
                        grade=student.grade
                    )

                return queryset.none()

            except Student.DoesNotExist:
                pass

        grade_id = self.request.query_params.get(
            "grade"
        )

        if grade_id:
            queryset = queryset.filter(
                grade_id=grade_id
            )

        return queryset


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChapterSerializer

    def get_queryset(self):
        queryset = Chapter.objects.select_related(
            "subject",
            "subject__grade"
        ).all()

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

        subject_id = self.request.query_params.get(
            "subject"
        )

        if subject_id:
            queryset = queryset.filter(
                subject_id=subject_id
            )

        return queryset


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TopicSerializer

    def get_queryset(self):
        queryset = Topic.objects.select_related(
            "chapter",
            "chapter__subject",
            "chapter__subject__grade"
        ).all()

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

        chapter_id = self.request.query_params.get(
            "chapter"
        )

        if chapter_id:
            queryset = queryset.filter(
                chapter_id=chapter_id
            )

        return queryset


class NoteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NoteSerializer

    def get_queryset(self):
        queryset = Note.objects.select_related(
            "chapter",
            "chapter__subject"
        ).all()

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

        chapter_id = self.request.query_params.get(
            "chapter"
        )

        if chapter_id:
            queryset = queryset.filter(
                chapter_id=chapter_id
            )

        return queryset


class LearningContentViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = LearningContentSerializer

    def get_queryset(self):
        queryset = LearningContent.objects.select_related(
            "topic",
            "topic__chapter",
            "topic__chapter__subject",
            "topic__chapter__subject__grade"
        ).all()

        if self.request.user.is_authenticated:

            try:
                student = self.request.user.student

                if student.grade:
                    queryset = queryset.filter(
                        topic__chapter__subject__grade=
                        student.grade
                    )

                else:
                    return queryset.none()

            except Student.DoesNotExist:
                return queryset.none()

        topic_id = self.request.query_params.get(
            "topic"
        )

        if topic_id:
            queryset = queryset.filter(
                topic_id=topic_id
            )

        return queryset