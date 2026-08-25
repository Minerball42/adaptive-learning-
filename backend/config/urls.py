from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/auth/",
        include("users.urls"),
    ),

    path(
        "api/courses/",
        include("courses.urls"),
    ),

    path(
        "api/quizzes/",
        include("quizzes.urls"),
    ),

    path(
        "api/progress/",
        include("progress.urls"),
    ),

    path(
        "api/teacher/",
        include("users.teacher_urls"),
    ),

    path(
        "api/sync/",
        include("offline_sync.urls"),
    ),
]