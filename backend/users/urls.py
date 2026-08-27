from django.urls import path

from .views import (
    AssignStudentGradeView,
    StudentLoginView,
    StudentProfileView,
    StudentRegisterView,
    StudentSubjectSelectionView,
    TeacherLoginView,
)


urlpatterns = [
    path(
        "register/",
        StudentRegisterView.as_view(),
        name="student-register",
    ),

    path(
        "login/",
        StudentLoginView.as_view(),
        name="student-login",
    ),

    path(
        "teacher/login/",
        TeacherLoginView.as_view(),
        name="teacher-login",
    ),

    path(
        "profile/",
        StudentProfileView.as_view(),
        name="student-profile",
    ),

    path(
        "subjects/",
        StudentSubjectSelectionView.as_view(),
        name="student-subject-selection",
    ),

    path(
        "students/<int:student_id>/grade/",
        AssignStudentGradeView.as_view(),
        name="assign-student-grade",
    ),
]