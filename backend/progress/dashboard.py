from .access import get_allowed_subject_ids
from .chapter_progress import build_chapter_progress
from .learning_path import build_learning_path
from .subject_progress import build_subject_progress
from .services import build_student_recommendations
from .models import QuizAttempt


# ============================================================
# RECENT ACTIVITY
# ============================================================


def build_recent_activity(
    student,
    limit=5,
):
    """
    Return the student's latest quiz attempts.

    Only attempts from subjects currently available
    to the student are included.
    """

    if (
        student is None
        or not student.grade_id
    ):
        return []

    allowed_subject_ids = (
        get_allowed_subject_ids(
            student
        )
    )

    attempts = (
        QuizAttempt.objects.filter(
            student=student,
            quiz__topic__chapter__subject_id__in=(
                allowed_subject_ids
            ),
        )
        .select_related(
            "quiz",
            "quiz__topic",
            "quiz__topic__chapter",
            "quiz__topic__chapter__subject",
        )
        .order_by(
            "-attempted_at",
            "-id",
        )[:limit]
    )

    results = []

    for attempt in attempts:

        if attempt.total_questions > 0:

            percentage = (
                attempt.score
                / attempt.total_questions
            ) * 100

        else:

            percentage = 0

        topic = (
            attempt.quiz.topic
        )

        chapter = (
            topic.chapter
        )

        subject = (
            chapter.subject
        )

        results.append(
            {
                "attempt_id": (
                    attempt.id
                ),

                "quiz_id": (
                    attempt.quiz.id
                ),

                "quiz_title": (
                    attempt.quiz.title
                ),

                "topic_id": (
                    topic.id
                ),

                "topic_name": (
                    topic.name
                ),

                "chapter_id": (
                    chapter.id
                ),

                "chapter_name": (
                    chapter.name
                ),

                "subject_id": (
                    subject.id
                ),

                "subject_name": (
                    subject.name
                ),

                "score": (
                    attempt.score
                ),

                "total_questions": (
                    attempt.total_questions
                ),

                "percentage": round(
                    percentage,
                    2,
                ),

                "attempted_at": (
                    attempt.attempted_at
                ),
            }
        )

    return results


# ============================================================
# CONTINUE LEARNING
# ============================================================


def get_continue_learning(
    learning_path,
):
    """
    Find the first unlocked topic that has not
    yet reached Strong mastery.
    """

    topics = (
        learning_path.get(
            "topics",
            [],
        )
    )

    for topic in topics:

        if (
            topic["unlocked"]
            and
            topic["level"] != "strong"
        ):

            return {
                "topic_id": (
                    topic["topic_id"]
                ),

                "topic_name": (
                    topic["topic_name"]
                ),

                "chapter_id": (
                    topic["chapter_id"]
                ),

                "chapter_name": (
                    topic["chapter_name"]
                ),

                "subject_id": (
                    topic["subject_id"]
                ),

                "subject_name": (
                    topic["subject_name"]
                ),

                "level": (
                    topic["level"]
                ),

                "mastery_score": (
                    topic["mastery_score"]
                ),

                "status": (
                    topic["status"]
                ),

                "action": (
                    "continue_learning"
                ),
            }

    return None


# ============================================================
# BUILD DASHBOARD
# ============================================================


def build_dashboard(
    student,
):
    """
    Build the complete student dashboard.

    Includes:

    - Student information
    - Overall topic progress
    - Subject progress
    - Chapter progress
    - Continue learning
    - Recommendations
    - Recent quiz activity
    """

    # ========================================================
    # LEARNING PATH
    # ========================================================

    learning_path = (
        build_learning_path(
            student
        )
    )

    # ========================================================
    # SUBJECT PROGRESS
    # ========================================================

    subject_progress = (
        build_subject_progress(
            student
        )
    )

    # ========================================================
    # CHAPTER PROGRESS
    # ========================================================

    chapter_progress = (
        build_chapter_progress(
            student
        )
    )

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    recommendations_data = (
        build_student_recommendations(
            student
        )
    )

    # ========================================================
    # RECENT ACTIVITY
    # ========================================================

    recent_activity = (
        build_recent_activity(
            student,
            limit=5,
        )
    )

    # ========================================================
    # CONTINUE LEARNING
    # ========================================================

    continue_learning = (
        get_continue_learning(
            learning_path
        )
    )

    # ========================================================
    # LEARNING PATH SUMMARY
    # ========================================================

    path_summary = (
        learning_path.get(
            "summary",
            {},
        )
    )

    total_topics = (
        path_summary.get(
            "total_topics",
            0,
        )
    )

    completed_topics = (
        path_summary.get(
            "completed",
            0,
        )
    )

    available_topics = (
        path_summary.get(
            "available",
            0,
        )
    )

    locked_topics = (
        path_summary.get(
            "locked",
            0,
        )
    )

    if total_topics > 0:

        topic_completion_percentage = (
            completed_topics
            / total_topics
        ) * 100

    else:

        topic_completion_percentage = 0

    # ========================================================
    # CHAPTER SUMMARY
    # ========================================================

    chapter_summary = (
        chapter_progress.get(
            "summary",
            {},
        )
    )

    # ========================================================
    # TOP RECOMMENDATIONS
    # ========================================================

    all_recommendations = (
        recommendations_data.get(
            "recommendations",
            [],
        )
    )

    active_recommendations = [
        recommendation
        for recommendation
        in all_recommendations
        if (
            recommendation["level"]
            != "strong"
        )
    ]

    top_recommendations = (
        active_recommendations[:3]
    )

    # ========================================================
    # DASHBOARD STATUS
    # ========================================================

    if (
        total_topics > 0
        and
        completed_topics == total_topics
    ):

        dashboard_status = (
            "all_available_topics_completed"
        )

    elif continue_learning:

        dashboard_status = (
            "learning_in_progress"
        )

    else:

        dashboard_status = (
            "ready_to_start"
        )

    # ========================================================
    # STUDENT INFORMATION
    # ========================================================

    user = (
        student.user
    )

    grade_name = None

    if student.grade:

        grade_name = (
            student.grade.name
        )

    school = getattr(
        student,
        "school",
        "",
    )

    preferred_language = getattr(
        student,
        "preferred_language",
        "English",
    )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "student": {
            "username": (
                user.username
            ),

            "email": (
                user.email
            ),

            "grade": (
                grade_name
            ),

            "school": (
                school
            ),

            "preferred_language": (
                preferred_language
            ),
        },

        "status": (
            dashboard_status
        ),

        "overview": {
            "total_topics": (
                total_topics
            ),

            "completed_topics": (
                completed_topics
            ),

            "available_topics": (
                available_topics
            ),

            "locked_topics": (
                locked_topics
            ),

            "topic_completion_percentage": round(
                topic_completion_percentage,
                2,
            ),

            "total_chapters": (
                chapter_summary.get(
                    "total_chapters",
                    0,
                )
            ),

            "completed_chapters": (
                chapter_summary.get(
                    "completed_chapters",
                    0,
                )
            ),

            "in_progress_chapters": (
                chapter_summary.get(
                    "in_progress_chapters",
                    0,
                )
            ),

            "chapter_completion_percentage": (
                chapter_summary.get(
                    "overall_completion_percentage",
                    0,
                )
            ),
        },

        # ----------------------------------------------------
        # SUBJECT PROGRESS FOR FRONTEND CARDS
        # ----------------------------------------------------

        "subject_progress": (
            subject_progress.get(
                "subjects",
                [],
            )
        ),

        "continue_learning": (
            continue_learning
        ),

        "recommendations": (
            top_recommendations
        ),

        "chapters": (
            chapter_progress.get(
                "chapters",
                [],
            )
        ),

        "recent_activity": (
            recent_activity
        ),
    }