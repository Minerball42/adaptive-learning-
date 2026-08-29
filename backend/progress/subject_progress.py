from courses.models import Topic

from .access import get_allowed_subjects
from .services import (
    build_mastery_data,
    get_student_topic_stats,
)


# ============================================================
# EMPTY RESPONSE
# ============================================================


def empty_subject_progress():
    """
    Return an empty subject-progress response.
    """

    return {
        "summary": {
            "total_subjects": 0,
            "completed_subjects": 0,
            "in_progress_subjects": 0,
            "not_started_subjects": 0,
        },
        "subjects": [],
    }


# ============================================================
# BUILD SUBJECT PROGRESS
# ============================================================


def build_subject_progress(student):
    """
    Build progress information for every subject
    currently available to the student.

    Allowed subjects include:

    - Core subjects
    - Selected language subjects
    - Selected optional subjects
    """

    if (
        student is None
        or not student.grade_id
    ):
        return empty_subject_progress()

    # ========================================================
    # ALLOWED SUBJECTS
    # ========================================================

    subjects = list(
        get_allowed_subjects(
            student
        )
    )

    # ========================================================
    # STUDENT PERFORMANCE
    # ========================================================

    stats = (
        get_student_topic_stats(
            student
        )
    )

    subject_results = []

    completed_subjects = 0
    in_progress_subjects = 0
    not_started_subjects = 0

    # ========================================================
    # PROCESS SUBJECTS
    # ========================================================

    for subject in subjects:

        topics = list(
            Topic.objects.filter(
                chapter__subject=subject
            )
            .select_related(
                "chapter",
                "chapter__subject",
            )
            .order_by(
                "chapter__chapter_number",
                "id",
            )
        )

        total_topics = len(
            topics
        )

        started_topics = 0
        completed_topics = 0

        mastery_scores = []

        # ====================================================
        # PROCESS TOPICS
        # ====================================================

        for topic in topics:

            topic_stats = (
                stats.get(
                    topic.id
                )
            )

            # ------------------------------------------------
            # NOT STARTED
            # ------------------------------------------------

            if not topic_stats:

                mastery_score = 0
                level = "not_started"

            # ------------------------------------------------
            # STARTED
            # ------------------------------------------------

            else:

                mastery = (
                    build_mastery_data(
                        topic_stats
                    )
                )

                mastery_score = (
                    mastery[
                        "mastery_score"
                    ]
                )

                level = (
                    mastery[
                        "level"
                    ]
                )

            mastery_scores.append(
                mastery_score
            )

            if level != "not_started":
                started_topics += 1

            if level == "strong":
                completed_topics += 1

        # ====================================================
        # COMPLETION PERCENTAGE
        # ====================================================

        if total_topics > 0:

            completion_percentage = (
                completed_topics
                / total_topics
            ) * 100

        else:

            completion_percentage = 0

        # ====================================================
        # AVERAGE MASTERY
        # ====================================================

        if mastery_scores:

            average_mastery = (
                sum(
                    mastery_scores
                )
                / len(
                    mastery_scores
                )
            )

        else:

            average_mastery = 0

        # ====================================================
        # SUBJECT STATUS
        # ====================================================

        if (
            total_topics > 0
            and
            completed_topics == total_topics
        ):

            subject_status = (
                "completed"
            )

            completed_subjects += 1

        elif started_topics > 0:

            subject_status = (
                "in_progress"
            )

            in_progress_subjects += 1

        else:

            subject_status = (
                "not_started"
            )

            not_started_subjects += 1

        # ====================================================
        # CHAPTER COUNT
        # ====================================================

        total_chapters = (
            subject.chapters.filter(
                topics__isnull=False
            )
            .distinct()
            .count()
        )

        # ====================================================
        # RESULT
        # ====================================================

        subject_results.append(
            {
                "subject_id": (
                    subject.id
                ),

                "subject_name": (
                    subject.name
                ),

                "subject_type": (
                    subject.subject_type
                ),

                "subject_type_display": (
                    subject.get_subject_type_display()
                ),

                "language": (
                    subject.language
                ),

                "status": (
                    subject_status
                ),

                "total_chapters": (
                    total_chapters
                ),

                "total_topics": (
                    total_topics
                ),

                "started_topics": (
                    started_topics
                ),

                "completed_topics": (
                    completed_topics
                ),

                "remaining_topics": (
                    total_topics
                    - completed_topics
                ),

                "completion_percentage": round(
                    completion_percentage,
                    2,
                ),

                "average_mastery": round(
                    average_mastery,
                    2,
                ),
            }
        )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "summary": {
            "total_subjects": (
                len(subject_results)
            ),

            "completed_subjects": (
                completed_subjects
            ),

            "in_progress_subjects": (
                in_progress_subjects
            ),

            "not_started_subjects": (
                not_started_subjects
            ),
        },

        "subjects": (
            subject_results
        ),
    }