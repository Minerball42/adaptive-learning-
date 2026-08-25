from django.urls import path

from .views import (
    OfflineBatchSyncView,
    OfflineQuizAttemptSyncView,
    OfflineSyncStatusView,
)


urlpatterns = [
    path(
        "quiz-attempts/",
        OfflineQuizAttemptSyncView.as_view(),
        name="offline-quiz-attempt-sync",
    ),

    path(
        "batch/",
        OfflineBatchSyncView.as_view(),
        name="offline-batch-sync",
    ),

    path(
        "status/",
        OfflineSyncStatusView.as_view(),
        name="offline-sync-status",
    ),
]