from rest_framework.routers import DefaultRouter

from .views import (
    BoardViewSet,
    AcademicYearViewSet,
    GradeViewSet,
    SubjectViewSet,
    ChapterViewSet,
    TopicViewSet,
    NoteViewSet,
    LearningContentViewSet,
)


router = DefaultRouter()


router.register(
    "boards",
    BoardViewSet,
    basename="board"
)


router.register(
    "academic-years",
    AcademicYearViewSet,
    basename="academic-year"
)


router.register(
    "grades",
    GradeViewSet,
    basename="grade"
)


router.register(
    "subjects",
    SubjectViewSet,
    basename="subject"
)


router.register(
    "chapters",
    ChapterViewSet,
    basename="chapter"
)


router.register(
    "topics",
    TopicViewSet,
    basename="topic"
)


router.register(
    "notes",
    NoteViewSet,
    basename="note"
)


router.register(
    "learning-content",
    LearningContentViewSet,
    basename="learning-content"
)


urlpatterns = router.urls