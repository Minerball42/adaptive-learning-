from courses.models import Topic

from .access import get_allowed_subject_ids
from .services import get_topic_mastery


# ============================================================
# SUBJECT ACCESS
# ============================================================


def student_can_access_topic(
    student,
    topic,
):
    """
    Return True only when the topic belongs to one
    of the student's allowed subjects.
    """

    if (
        student is None
        or not student.grade_id
    ):
        return False

    return (
        get_allowed_subject_ids(
            student
        )
        .filter(
            id=topic.chapter.subject_id
        )
        .exists()
    )


# ============================================================
# ORDERED LEARNING PATH
# ============================================================


def get_ordered_topics(student):
    """
    Return topics belonging only to the student's
    allowed subjects.

    Allowed subjects include:

    - Core subjects
    - Student-selected language subjects
    - Student-selected optional subjects

    Topics are returned in curriculum order.
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

    return list(
        Topic.objects.filter(
            chapter__subject_id__in=(
                allowed_subject_ids
            )
        )
        .select_related(
            "chapter",
            "chapter__subject",
        )
        .order_by(
            "chapter__subject__display_order",
            "chapter__subject__name",
            "chapter__chapter_number",
            "id",
        )
    )


# ============================================================
# PREVIOUS TOPIC
# ============================================================


def get_previous_topic(
    student,
    topic,
):
    """
    Find the topic immediately before the supplied
    topic within the same subject.

    Only topics belonging to a subject the student
    is allowed to access are considered.
    """

    if not student_can_access_topic(
        student,
        topic,
    ):
        return None

    topics = list(
        Topic.objects.filter(
            chapter__subject=(
                topic.chapter.subject
            )
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

    for index, current_topic in enumerate(
        topics
    ):

        if current_topic.id == topic.id:

            if index == 0:
                return None

            return topics[
                index - 1
            ]

    return None


# ============================================================
# TOPIC UNLOCKING
# ============================================================


def is_topic_unlocked(
    student,
    topic,
):
    """
    Determine whether a student is allowed to
    access a topic.

    Rules:

    1. The topic must belong to one of the
       student's allowed subjects.

    2. The first topic in each subject is
       automatically unlocked.

    3. Every later topic requires the previous
       topic to reach Strong mastery.
    """

    # --------------------------------------------------------
    # SUBJECT ACCESS
    # --------------------------------------------------------

    if not student_can_access_topic(
        student,
        topic,
    ):

        return {
            "unlocked": False,
            "previous_topic": None,
            "reason": (
                "subject_not_allowed"
            ),
        }

    # --------------------------------------------------------
    # PREVIOUS TOPIC
    # --------------------------------------------------------

    previous_topic = get_previous_topic(
        student,
        topic,
    )

    # First topic in the subject.
    if previous_topic is None:

        return {
            "unlocked": True,
            "previous_topic": None,
            "reason": "first_topic",
        }

    # --------------------------------------------------------
    # PREVIOUS TOPIC MASTERY
    # --------------------------------------------------------

    previous_mastery = (
        get_topic_mastery(
            student,
            previous_topic,
        )
    )

    previous_topic_data = {
        "id": (
            previous_topic.id
        ),

        "name": (
            previous_topic.name
        ),

        "level": (
            previous_mastery[
                "level"
            ]
        ),

        "mastery_score": (
            previous_mastery[
                "mastery_score"
            ]
        ),
    }

    # --------------------------------------------------------
    # UNLOCKED
    # --------------------------------------------------------

    if (
        previous_mastery["level"]
        == "strong"
    ):

        return {
            "unlocked": True,

            "previous_topic": (
                previous_topic_data
            ),

            "reason": (
                "previous_topic_mastered"
            ),
        }

    # --------------------------------------------------------
    # LOCKED
    # --------------------------------------------------------

    return {
        "unlocked": False,

        "previous_topic": (
            previous_topic_data
        ),

        "reason": (
            "previous_topic_not_mastered"
        ),
    }


# ============================================================
# BUILD LEARNING PATH
# ============================================================


def build_learning_path(student):
    """
    Build the complete topic-by-topic learning
    path for the student's allowed subjects.

    Returned topic states:

    completed
        Topic reached Strong mastery.

    available
        Topic is unlocked but not yet mastered.

    locked
        Previous topic has not reached Strong
        mastery.
    """

    topics = get_ordered_topics(
        student
    )

    path = []

    completed_count = 0
    available_count = 0
    locked_count = 0

    # ========================================================
    # PROCESS TOPICS
    # ========================================================

    for topic in topics:

        mastery = get_topic_mastery(
            student,
            topic,
        )

        unlock = is_topic_unlocked(
            student,
            topic,
        )

        # ----------------------------------------------------
        # COMPLETED
        # ----------------------------------------------------

        if mastery["level"] == "strong":

            status = "completed"

            completed_count += 1

        # ----------------------------------------------------
        # AVAILABLE
        # ----------------------------------------------------

        elif unlock["unlocked"]:

            status = "available"

            available_count += 1

        # ----------------------------------------------------
        # LOCKED
        # ----------------------------------------------------

        else:

            status = "locked"

            locked_count += 1

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        path.append(
            {
                "topic_id": (
                    topic.id
                ),

                "topic_name": (
                    topic.name
                ),

                "chapter_id": (
                    topic.chapter.id
                ),

                "chapter_name": (
                    topic.chapter.name
                ),

                "subject_id": (
                    topic.chapter.subject.id
                ),

                "subject_name": (
                    topic.chapter.subject.name
                ),

                "status": (
                    status
                ),

                "unlocked": (
                    unlock[
                        "unlocked"
                    ]
                ),

                "level": (
                    mastery[
                        "level"
                    ]
                ),

                "mastery_score": (
                    mastery[
                        "mastery_score"
                    ]
                ),

                "percentage": (
                    mastery[
                        "percentage"
                    ]
                ),

                "previous_topic": (
                    unlock[
                        "previous_topic"
                    ]
                ),
            }
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    total_topics = len(
        topics
    )

    if total_topics > 0:

        completion_percentage = (
            completed_count
            / total_topics
        ) * 100

    else:

        completion_percentage = 0

    return {
        "summary": {
            "total_topics": (
                total_topics
            ),

            "completed": (
                completed_count
            ),

            "available": (
                available_count
            ),

            "locked": (
                locked_count
            ),

            "completion_percentage": round(
                completion_percentage,
                2,
            ),
        },

        "topics": (
            path
        ),
    }