from django.urls import path

from .views import (
    SubmitQuizView,
    QuizAttemptResultsView,
    TopicPerformanceView,
    MyTopicPerformanceView,
    MyRecommendationsView,
)

from .learning_path_views import (
    MyLearningPathView,
)

from .chapter_progress_views import (
    MyChapterProgressView,
)

from .dashboard_views import (
    MyDashboardView,
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

    path(
        "my-recommendations/",
        MyRecommendationsView.as_view(),
        name="my-recommendations",
    ),

    path(
        "learning-path/",
        MyLearningPathView.as_view(),
        name="my-learning-path",
    ),

    path(
        "chapter-progress/",
        MyChapterProgressView.as_view(),
        name="my-chapter-progress",
    ),

    path(
        "dashboard/",
        MyDashboardView.as_view(),
        name="my-dashboard",
    ),
]