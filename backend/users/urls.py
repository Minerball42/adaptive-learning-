
from django.urls import path

from .views import (
    StudentLoginView,
    StudentProfileView,
    StudentRegisterView,
    TeacherLoginView,
    AssignStudentGradeView,
)

urlpatterns = [
    path("register/", StudentRegisterView.as_view(), name="student-register"),
    path("login/", StudentLoginView.as_view(), name="student-login"),
    path("teacher/login/", TeacherLoginView.as_view(), name="teacher-login"),
    path("profile/", StudentProfileView.as_view(), name="student-profile"),

    path(
        "students/<int:student_id>/grade/",
        AssignStudentGradeView.as_view(),
        name="assign-student-grade",
    ),
]