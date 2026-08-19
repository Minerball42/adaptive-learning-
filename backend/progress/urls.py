from django.urls import path

from .views import (
    SubmitQuizView,
    QuizAttemptResultsView,
    TopicPerformanceView,
    MyTopicPerformanceView,
)

urlpatterns = [
    path(
        "submit/",
        SubmitQuizView.as_view(),
        name="submit-quiz",
    ),
    path(
        "attempts/",
        QuizAttemptResultsView.as_view(),
        name="quiz-attempt-results",
    ),
    path(
        "topic-performance/",
        TopicPerformanceView.as_view(),
        name="topic-performance",
    ),
    path(
        "my-topic-performance/",
        MyTopicPerformanceView.as_view(),
        name="my-topic-performance",
    ),
]