from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    QuizViewSet,
    QuestionViewSet,
    AdaptiveQuizView,
    AdaptiveQuizSubmitView,
)


router = DefaultRouter()

router.register(
    "quizzes",
    QuizViewSet,
    basename="quiz",
)

router.register(
    "questions",
    QuestionViewSet,
    basename="question",
)


urlpatterns = [
    path(
        "adaptive/submit/",
        AdaptiveQuizSubmitView.as_view(),
        name="adaptive-quiz-submit",
    ),

    path(
        "adaptive/",
        AdaptiveQuizView.as_view(),
        name="adaptive-quiz",
    ),
]


urlpatterns += router.urls