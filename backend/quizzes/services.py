from progress.services import (
    get_topic_mastery,
)

from .models import Question


def get_difficulty_for_level(level):
    """
    Convert mastery level into adaptive
    question difficulty.
    """

    if level in [
        "not_started",
        "weak",
    ]:
        return 1

    if level == "developing":
        return 2

    return 3


def get_difficulty_name(value):
    """
    Convert difficulty number into text.
    """

    names = {
        1: "easy",
        2: "medium",
        3: "hard",
    }

    return names.get(
        value,
        "easy",
    )


def get_fallback_order(
    target_difficulty
):
    """
    Select the closest difficulty when
    there are not enough questions.
    """

    if target_difficulty == 1:
        return [2, 3]

    if target_difficulty == 2:
        return [1, 3]

    return [2, 1]


def select_adaptive_questions(
    quiz,
    target_difficulty,
    limit=3,
):
    """
    Select questions at the target difficulty.

    If there are not enough questions,
    use the nearest difficulty as fallback.
    """

    questions = list(
        Question.objects.filter(
            quiz=quiz,
            difficulty=target_difficulty,
        )
        .order_by("id")[:limit]
    )

    fallback_used = False

    if len(questions) < limit:

        fallback_used = True

        selected_ids = [
            question.id
            for question in questions
        ]

        remaining = (
            limit - len(questions)
        )

        for difficulty in (
            get_fallback_order(
                target_difficulty
            )
        ):

            if remaining <= 0:
                break

            extra_questions = list(
                Question.objects.filter(
                    quiz=quiz,
                    difficulty=difficulty,
                )
                .exclude(
                    id__in=selected_ids
                )
                .order_by("id")[
                    :remaining
                ]
            )

            questions.extend(
                extra_questions
            )

            selected_ids.extend(
                question.id
                for question
                in extra_questions
            )

            remaining = (
                limit - len(questions)
            )

    actual_difficulties = sorted(
        {
            question.difficulty
            for question in questions
        }
    )

    return {
        "questions": questions,

        "fallback_used": (
            fallback_used
        ),

        "actual_difficulties": (
            actual_difficulties
        ),
    }