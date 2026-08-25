from courses.models import Topic

from .services import get_topic_mastery


def get_ordered_topics(student):
    """
    Return topics belonging to the student's grade
    in curriculum order.
    """

    if not student.grade:
        return []

    return list(
        Topic.objects.filter(
            chapter__subject__grade=student.grade
        )
        .select_related(
            "chapter",
            "chapter__subject",
        )
        .order_by(
            "chapter__subject__name",
            "chapter__chapter_number",
            "id",
        )
    )


def get_previous_topic(student, topic):
    """
    Find the topic immediately before the supplied
    topic within the same subject.
    """

    topics = list(
        Topic.objects.filter(
            chapter__subject=topic.chapter.subject,
            chapter__subject__grade=student.grade,
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

    for index, current_topic in enumerate(topics):

        if current_topic.id == topic.id:

            if index == 0:
                return None

            return topics[index - 1]

    return None


def is_topic_unlocked(student, topic):
    """
    First topic in a subject is always unlocked.

    Every later topic requires the previous topic
    to have reached Strong mastery.
    """

    previous_topic = get_previous_topic(
        student,
        topic,
    )

    if previous_topic is None:

        return {
            "unlocked": True,
            "previous_topic": None,
            "reason": "first_topic",
        }

    previous_mastery = get_topic_mastery(
        student,
        previous_topic,
    )

    if previous_mastery["level"] == "strong":

        return {
            "unlocked": True,

            "previous_topic": {
                "id": previous_topic.id,
                "name": previous_topic.name,
                "level": previous_mastery["level"],
                "mastery_score": (
                    previous_mastery[
                        "mastery_score"
                    ]
                ),
            },

            "reason": (
                "previous_topic_mastered"
            ),
        }

    return {
        "unlocked": False,

        "previous_topic": {
            "id": previous_topic.id,
            "name": previous_topic.name,
            "level": previous_mastery["level"],
            "mastery_score": (
                previous_mastery[
                    "mastery_score"
                ]
            ),
        },

        "reason": (
            "previous_topic_not_mastered"
        ),
    }


def build_learning_path(student):
    """
    Build the complete topic-by-topic learning
    path for the student's grade.
    """

    topics = get_ordered_topics(
        student
    )

    path = []

    completed_count = 0
    available_count = 0
    locked_count = 0

    for topic in topics:

        mastery = get_topic_mastery(
            student,
            topic,
        )

        unlock = is_topic_unlocked(
            student,
            topic,
        )

        if mastery["level"] == "strong":

            status = "completed"
            completed_count += 1

        elif unlock["unlocked"]:

            status = "available"
            available_count += 1

        else:

            status = "locked"
            locked_count += 1

        path.append(
            {
                "topic_id": topic.id,
                "topic_name": topic.name,

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

                "status": status,

                "unlocked": (
                    unlock["unlocked"]
                ),

                "level": (
                    mastery["level"]
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

            "completion_percentage": (
                round(
                    completion_percentage,
                    2,
                )
            ),
        },

        "topics": path,
    }