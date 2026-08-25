from courses.models import Chapter

from .services import get_topic_mastery


def build_chapter_progress(student):
    """
    Build chapter-level progress for the
    student's assigned grade.

    Only chapters that currently contain
    topics are included.
    """

    if not student.grade:
        return {
            "summary": {
                "total_chapters": 0,
                "completed_chapters": 0,
                "in_progress_chapters": 0,
                "not_started_chapters": 0,
                "overall_completion_percentage": 0,
            },
            "chapters": [],
        }

    chapters = (
        Chapter.objects.filter(
            subject__grade=student.grade,
            topics__isnull=False,
        )
        .select_related(
            "subject",
            "subject__grade",
        )
        .prefetch_related(
            "topics"
        )
        .distinct()
        .order_by(
            "subject__name",
            "chapter_number",
        )
    )

    chapter_results = []

    completed_chapters = 0
    in_progress_chapters = 0
    not_started_chapters = 0

    # ---------------------------------------------------------
    # PROCESS EACH CHAPTER
    # ---------------------------------------------------------

    for chapter in chapters:

        topics = list(
            chapter.topics.all().order_by("id")
        )

        total_topics = len(topics)

        completed_topics = 0
        started_topics = 0

        mastery_scores = []

        topic_results = []

        # -----------------------------------------------------
        # PROCESS TOPICS
        # -----------------------------------------------------

        for topic in topics:

            mastery = get_topic_mastery(
                student,
                topic,
            )

            level = mastery["level"]

            if level != "not_started":
                started_topics += 1

            if level == "strong":
                completed_topics += 1

            mastery_scores.append(
                mastery["mastery_score"]
            )

            topic_results.append(
                {
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "level": level,
                    "mastery_score": (
                        mastery["mastery_score"]
                    ),
                    "percentage": (
                        mastery["percentage"]
                    ),
                    "attempt_count": (
                        mastery["attempt_count"]
                    ),
                }
            )

        # -----------------------------------------------------
        # COMPLETION PERCENTAGE
        # -----------------------------------------------------

        if total_topics > 0:
            completion_percentage = (
                completed_topics
                / total_topics
            ) * 100
        else:
            completion_percentage = 0

        # -----------------------------------------------------
        # AVERAGE MASTERY
        # -----------------------------------------------------

        if mastery_scores:
            average_mastery = (
                sum(mastery_scores)
                / len(mastery_scores)
            )
        else:
            average_mastery = 0

        # -----------------------------------------------------
        # CHAPTER STATUS
        # -----------------------------------------------------

        if (
            total_topics > 0
            and completed_topics == total_topics
        ):
            chapter_status = "completed"
            completed_chapters += 1

        elif started_topics > 0:
            chapter_status = "in_progress"
            in_progress_chapters += 1

        else:
            chapter_status = "not_started"
            not_started_chapters += 1

        # -----------------------------------------------------
        # RESULT
        # -----------------------------------------------------

        chapter_results.append(
            {
                "chapter_id": chapter.id,
                "chapter_number": (
                    chapter.chapter_number
                ),
                "chapter_name": chapter.name,

                "subject_id": (
                    chapter.subject.id
                ),
                "subject_name": (
                    chapter.subject.name
                ),

                "status": chapter_status,

                "total_topics": total_topics,

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

                "topics": topic_results,
            }
        )

    # ---------------------------------------------------------
    # OVERALL SUMMARY
    # ---------------------------------------------------------

    total_chapters = len(
        chapter_results
    )

    if total_chapters > 0:
        overall_completion_percentage = (
            completed_chapters
            / total_chapters
        ) * 100
    else:
        overall_completion_percentage = 0

    return {
        "summary": {
            "total_chapters": (
                total_chapters
            ),

            "completed_chapters": (
                completed_chapters
            ),

            "in_progress_chapters": (
                in_progress_chapters
            ),

            "not_started_chapters": (
                not_started_chapters
            ),

            "overall_completion_percentage": round(
                overall_completion_percentage,
                2,
            ),
        },

        "chapters": chapter_results,
    }