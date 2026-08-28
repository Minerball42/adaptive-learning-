from django.db.models import Q

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


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def get_student_from_request(request):
    """
    Return the Student object for the authenticated user.

    Returns None when:
    - user is not authenticated
    - authenticated user is not a student
    """

    if not request.user.is_authenticated:
        return None

    try:
        return request.user.student

    except Student.DoesNotExist:
        return None


def get_allowed_subject_ids(student):
    """
    Return subject IDs the student is allowed to access.

    A student can access:

    1. All core subjects for their grade
    2. Subjects selected through selected_subjects

    This ensures Mathematics, Science and Social Science remain
    available even if an older student record does not yet have
    those core subjects stored in selected_subjects.
    """

    if not student or not student.grade_id:
        return Subject.objects.none().values_list(
            "id",
            flat=True,
        )

    selected_subject_ids = (
        student.selected_subjects.values_list(
            "id",
            flat=True,
        )
    )

    return (
        Subject.objects.filter(
            grade_id=student.grade_id
        )
        .filter(
            Q(subject_type="core")
            | Q(
                id__in=selected_subject_ids
            )
        )
        .values_list(
            "id",
            flat=True,
        )
    )


# ============================================================
# BOARD
# ============================================================


class BoardViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = BoardSerializer

    queryset = Board.objects.filter(
        is_active=True
    )


# ============================================================
# ACADEMIC YEAR
# ============================================================


class AcademicYearViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = AcademicYearSerializer

    def get_queryset(self):

        queryset = (
            AcademicYear.objects
            .select_related(
                "board"
            )
            .all()
        )

        board_id = (
            self.request.query_params.get(
                "board"
            )
        )

        if board_id:
            queryset = queryset.filter(
                board_id=board_id
            )

        return queryset


# ============================================================
# GRADE
# ============================================================


class GradeViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = GradeSerializer

    def get_queryset(self):

        queryset = (
            Grade.objects
            .select_related(
                "academic_year",
                "academic_year__board",
            )
            .all()
        )

        academic_year_id = (
            self.request.query_params.get(
                "academic_year"
            )
        )

        if academic_year_id:
            queryset = queryset.filter(
                academic_year_id=(
                    academic_year_id
                )
            )

        board_id = (
            self.request.query_params.get(
                "board"
            )
        )

        if board_id:
            queryset = queryset.filter(
                academic_year__board_id=(
                    board_id
                )
            )

        return queryset


# ============================================================
# SUBJECT
# ============================================================


class SubjectViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = SubjectSerializer

    def get_queryset(self):

        queryset = (
            Subject.objects
            .select_related(
                "grade"
            )
            .all()
        )

        student = get_student_from_request(
            self.request
        )

        # --------------------------------------------------------
        # AUTHENTICATED STUDENT
        # --------------------------------------------------------

        if student:

            if not student.grade_id:
                return queryset.none()

            allowed_subject_ids = (
                get_allowed_subject_ids(
                    student
                )
            )

            return queryset.filter(
                id__in=allowed_subject_ids
            )

        # --------------------------------------------------------
        # NON-STUDENT / ANONYMOUS FILTER
        # --------------------------------------------------------

        grade_id = (
            self.request.query_params.get(
                "grade"
            )
        )

        if grade_id:
            queryset = queryset.filter(
                grade_id=grade_id
            )

        return queryset


# ============================================================
# CHAPTER
# ============================================================


class ChapterViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = ChapterSerializer

    def get_queryset(self):

        queryset = (
            Chapter.objects
            .select_related(
                "subject",
                "subject__grade",
            )
            .all()
        )

        student = get_student_from_request(
            self.request
        )

        # --------------------------------------------------------
        # STUDENT ACCESS CONTROL
        # --------------------------------------------------------

        if student:

            if not student.grade_id:
                return queryset.none()

            allowed_subject_ids = (
                get_allowed_subject_ids(
                    student
                )
            )

            queryset = queryset.filter(
                subject_id__in=(
                    allowed_subject_ids
                )
            )

        # --------------------------------------------------------
        # OPTIONAL SUBJECT FILTER
        # --------------------------------------------------------

        subject_id = (
            self.request.query_params.get(
                "subject"
            )
        )

        if subject_id:

            queryset = queryset.filter(
                subject_id=subject_id
            )

        return queryset


# ============================================================
# TOPIC
# ============================================================


class TopicViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = TopicSerializer

    def get_queryset(self):

        queryset = (
            Topic.objects
            .select_related(
                "chapter",
                "chapter__subject",
                "chapter__subject__grade",
            )
            .all()
        )

        student = get_student_from_request(
            self.request
        )

        # --------------------------------------------------------
        # STUDENT ACCESS CONTROL
        # --------------------------------------------------------

        if student:

            if not student.grade_id:
                return queryset.none()

            allowed_subject_ids = (
                get_allowed_subject_ids(
                    student
                )
            )

            queryset = queryset.filter(
                chapter__subject_id__in=(
                    allowed_subject_ids
                )
            )

        # --------------------------------------------------------
        # CHAPTER FILTER
        # --------------------------------------------------------

        chapter_id = (
            self.request.query_params.get(
                "chapter"
            )
        )

        if chapter_id:

            queryset = queryset.filter(
                chapter_id=chapter_id
            )

        return queryset


# ============================================================
# NOTES
# ============================================================


class NoteViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = NoteSerializer

    def get_queryset(self):

        queryset = (
            Note.objects
            .select_related(
                "chapter",
                "chapter__subject",
                "chapter__subject__grade",
            )
            .all()
        )

        student = get_student_from_request(
            self.request
        )

        # --------------------------------------------------------
        # STUDENT ACCESS CONTROL
        # --------------------------------------------------------

        if student:

            if not student.grade_id:
                return queryset.none()

            allowed_subject_ids = (
                get_allowed_subject_ids(
                    student
                )
            )

            queryset = queryset.filter(
                chapter__subject_id__in=(
                    allowed_subject_ids
                )
            )

        # --------------------------------------------------------
        # CHAPTER FILTER
        # --------------------------------------------------------

        chapter_id = (
            self.request.query_params.get(
                "chapter"
            )
        )

        if chapter_id:

            queryset = queryset.filter(
                chapter_id=chapter_id
            )

        return queryset


# ============================================================
# LEARNING CONTENT
# ============================================================


class LearningContentViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = (
        LearningContentSerializer
    )

    def get_queryset(self):

        queryset = (
            LearningContent.objects
            .select_related(
                "topic",
                "topic__chapter",
                "topic__chapter__subject",
                "topic__chapter__subject__grade",
            )
            .all()
        )

        student = get_student_from_request(
            self.request
        )

        # --------------------------------------------------------
        # STUDENT ACCESS CONTROL
        # --------------------------------------------------------

        if student:

            if not student.grade_id:
                return queryset.none()

            allowed_subject_ids = (
                get_allowed_subject_ids(
                    student
                )
            )

            queryset = queryset.filter(
                topic__chapter__subject_id__in=(
                    allowed_subject_ids
                )
            )

        # --------------------------------------------------------
        # TOPIC FILTER
        # --------------------------------------------------------

        topic_id = (
            self.request.query_params.get(
                "topic"
            )
        )

        if topic_id:

            queryset = queryset.filter(
                topic_id=topic_id
            )

        return queryset