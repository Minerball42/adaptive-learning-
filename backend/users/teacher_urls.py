from django.urls import path

from .teacher_views import (
    TeacherDashboardView,
    TeacherRecentAttemptsView,
    TeacherStudentProgressView,
    TeacherStudentsView,
    TeacherWeakTopicsView,
)


urlpatterns = [
    path(
        "dashboard/",
        TeacherDashboardView.as_view(),
        name="teacher-dashboard",
    ),

    path(
        "students/",
        TeacherStudentsView.as_view(),
        name="teacher-students",
    ),

    path(
        "students/<int:student_id>/progress/",
        TeacherStudentProgressView.as_view(),
        name="teacher-student-progress",
    ),

    path(
        "weak-topics/",
        TeacherWeakTopicsView.as_view(),
        name="teacher-weak-topics",
    ),

    path(
        "recent-attempts/",
        TeacherRecentAttemptsView.as_view(),
        name="teacher-recent-attempts",
    ),
]