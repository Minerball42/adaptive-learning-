from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    # API documentation
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui",
    ),

    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema"
        ),
        name="redoc",
    ),

    # Authentication
    path(
        "api/auth/",
        include("users.urls"),
    ),

    # Courses
    path(
        "api/courses/",
        include("courses.urls"),
    ),

    # Quizzes
    path(
        "api/quizzes/",
        include("quizzes.urls"),
    ),

    # Progress
    path(
        "api/progress/",
        include("progress.urls"),
    ),

    # Teacher
    path(
        "api/teacher/",
        include("users.teacher_urls"),
    ),

    # Offline sync
    path(
        "api/sync/",
        include("offline_sync.urls"),
    ),
]