from rest_framework.routers import DefaultRouter

from .views import (
    GradeViewSet,
    SubjectViewSet,
    ChapterViewSet,
    TopicViewSet,
    NoteViewSet,
    LearningContentViewSet,
)


router = DefaultRouter()

router.register("grades", GradeViewSet, basename="grade")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("chapters", ChapterViewSet, basename="chapter")
router.register("topics", TopicViewSet, basename="topic")
router.register("notes", NoteViewSet, basename="note")
router.register("learning-content",LearningContentViewSet,basename="learning-content")

urlpatterns = router.urls