from django.db.models import Q

from courses.models import Subject


def get_allowed_subject_ids(student):
    """
    Return the subject IDs that a student is
    allowed to access.

    Allowed subjects:

    1. All core subjects belonging to the
       student's grade.

    2. Subjects explicitly selected by the
       student.

    This mirrors the access rule used by the
    course APIs.
    """

    if (
        student is None
        or not student.grade_id
    ):
        return (
            Subject.objects
            .none()
            .values_list(
                "id",
                flat=True,
            )
        )

    selected_subject_ids = (
        student.selected_subjects
        .filter(
            grade_id=student.grade_id
        )
        .values_list(
            "id",
            flat=True,
        )
    )

    return (
        Subject.objects
        .filter(
            grade_id=student.grade_id
        )
        .filter(
            Q(
                subject_type="core"
            )
            |
            Q(
                id__in=selected_subject_ids
            )
        )
        .values_list(
            "id",
            flat=True,
        )
    )


def get_allowed_subjects(student):
    """
    Return the complete Subject queryset
    available to the student.
    """

    allowed_ids = (
        get_allowed_subject_ids(
            student
        )
    )

    return (
        Subject.objects
        .filter(
            id__in=allowed_ids
        )
        .select_related(
            "grade"
        )
        .order_by(
            "display_order",
            "name",
        )
    )