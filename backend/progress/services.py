from courses.models import Topic

from .models import QuizAttempt
from .access import get_allowed_subject_ids


# =========================================================
# MASTERY SETTINGS
# =========================================================

RECENT_ATTEMPT_WINDOW = 3

LIFETIME_WEIGHT = 0.70
RECENT_WEIGHT = 0.30

MIN_MEDIUM_QUESTIONS_FOR_GOOD = 3
MIN_HARD_QUESTIONS_FOR_STRONG = 3

MIN_MEDIUM_ACCURACY = 70
MIN_HARD_ACCURACY = 80


# =========================================================
# BASIC MASTERY LEVEL
# =========================================================

def get_mastery_level(mastery_score):
    """
    Raw mastery level based only on score.

    Final adaptive level may be limited by
    difficulty evidence.
    """

    if mastery_score < 50:
        return "weak"

    if mastery_score < 70:
        return "developing"

    if mastery_score < 85:
        return "good"

    return "strong"


# =========================================================
# WEIGHTED MASTERY SCORE
# =========================================================

def calculate_mastery_score(
    lifetime_percentage,
    recent_percentages,
):
    """
    Weighted mastery:

    70% lifetime performance
    30% recent performance
    """

    if not recent_percentages:
        return round(
            lifetime_percentage,
            2,
        )

    recent_values = recent_percentages[
        -RECENT_ATTEMPT_WINDOW:
    ]

    recent_average = (
        sum(recent_values)
        / len(recent_values)
    )

    mastery_score = (
        lifetime_percentage
        * LIFETIME_WEIGHT
        +
        recent_average
        * RECENT_WEIGHT
    )

    return round(
        mastery_score,
        2,
    )


# =========================================================
# DIFFICULTY PERFORMANCE
# =========================================================

def empty_difficulty_stats():

    return {
        1: {
            "correct": 0,
            "total": 0,
        },
        2: {
            "correct": 0,
            "total": 0,
        },
        3: {
            "correct": 0,
            "total": 0,
        },
    }


def calculate_accuracy(
    correct,
    total,
):

    if total == 0:
        return None

    return round(
        (correct / total) * 100,
        2,
    )


def build_difficulty_performance(
    difficulty_stats,
):
    """
    Return readable Easy/Medium/Hard
    performance information.
    """

    result = {}

    names = {
        1: "easy",
        2: "medium",
        3: "hard",
    }

    for difficulty, name in names.items():

        values = difficulty_stats[
            difficulty
        ]

        result[name] = {
            "correct": (
                values["correct"]
            ),

            "total": (
                values["total"]
            ),

            "percentage": (
                calculate_accuracy(
                    values["correct"],
                    values["total"],
                )
            ),
        }

    return result


# =========================================================
# ADAPTIVE LEVEL WITH DIFFICULTY GATES
# =========================================================

def determine_adaptive_level(
    mastery_score,
    difficulty_performance,
):
    """
    Mastery cannot advance based only on
    percentage.

    Rules:

    Weak:
        mastery < 50

    Developing:
        mastery >= 50

    Good:
        mastery >= 70
        AND sufficient Medium evidence

    Strong:
        mastery >= 85
        AND sufficient Hard evidence
    """

    # -----------------------------------------------------
    # WEAK
    # -----------------------------------------------------

    if mastery_score < 50:
        return "weak"

    medium = (
        difficulty_performance[
            "medium"
        ]
    )

    hard = (
        difficulty_performance[
            "hard"
        ]
    )

    # -----------------------------------------------------
    # STRONG GATE
    # -----------------------------------------------------

    if mastery_score >= 85:

        hard_percentage = (
            hard["percentage"]
        )

        if (
            hard["total"]
            >= MIN_HARD_QUESTIONS_FOR_STRONG
            and
            hard_percentage is not None
            and
            hard_percentage
            >= MIN_HARD_ACCURACY
        ):
            return "strong"

    # -----------------------------------------------------
    # GOOD GATE
    # -----------------------------------------------------

    if mastery_score >= 70:

        medium_percentage = (
            medium["percentage"]
        )

        if (
            medium["total"]
            >= MIN_MEDIUM_QUESTIONS_FOR_GOOD
            and
            medium_percentage is not None
            and
            medium_percentage
            >= MIN_MEDIUM_ACCURACY
        ):
            return "good"

        # Hard questions also prove that the
        # student has reached at least Good.
        if hard["total"] > 0:
            return "good"

    # -----------------------------------------------------
    # DEVELOPING
    # -----------------------------------------------------

    return "developing"


# =========================================================
# COLLECT TOPIC STATISTICS
# =========================================================

def get_student_topic_stats(student):
    """
    Collect quiz-attempt statistics only for
    subjects currently available to the student.

    Allowed subjects are:

    - Core subjects
    - Selected language subjects
    - Selected optional subjects
    """

    if (
        student is None
        or not student.grade_id
    ):
        return {}

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
        .prefetch_related(
            "answers__question"
        )
        .order_by(
            "attempted_at",
            "id",
        )
    )

    stats = {}

    # -----------------------------------------------------
    # PROCESS ATTEMPTS
    # -----------------------------------------------------

    for attempt in attempts:

        topic = (
            attempt.quiz.topic
        )

        if topic.id not in stats:

            stats[topic.id] = {
                "topic": topic,
                "correct": 0,
                "total": 0,
                "attempt_count": 0,
                "attempt_percentages": [],
                "difficulty_stats": (
                    empty_difficulty_stats()
                ),
            }

        topic_stats = (
            stats[
                topic.id
            ]
        )

        attempt_correct = 0
        attempt_total = 0

        # -------------------------------------------------
        # PROCESS ANSWERS
        # -------------------------------------------------

        for answer in (
            attempt.answers.all()
        ):

            attempt_total += 1

            topic_stats[
                "total"
            ] += 1

            difficulty = (
                answer.question.difficulty
            )

            if difficulty not in {
                1,
                2,
                3,
            }:
                difficulty = 1

            topic_stats[
                "difficulty_stats"
            ][difficulty]["total"] += 1

            if answer.is_correct:

                attempt_correct += 1

                topic_stats[
                    "correct"
                ] += 1

                topic_stats[
                    "difficulty_stats"
                ][difficulty]["correct"] += 1

        # -------------------------------------------------
        # ATTEMPT PERCENTAGE
        # -------------------------------------------------

        if attempt_total > 0:

            attempt_percentage = (
                attempt_correct
                / attempt_total
            ) * 100

            topic_stats[
                "attempt_percentages"
            ].append(
                round(
                    attempt_percentage,
                    2,
                )
            )

        topic_stats[
            "attempt_count"
        ] += 1

    return stats


# =========================================================
# BUILD MASTERY DATA
# =========================================================

def build_mastery_data(
    topic_stats,
):

    correct = topic_stats[
        "correct"
    ]

    total = topic_stats[
        "total"
    ]

    attempt_count = topic_stats[
        "attempt_count"
    ]

    attempt_percentages = (
        topic_stats[
            "attempt_percentages"
        ]
    )

    difficulty_stats = (
        topic_stats[
            "difficulty_stats"
        ]
    )

    # -----------------------------------------------------
    # NOT STARTED
    # -----------------------------------------------------

    if total == 0:

        return {
            "correct": 0,
            "total": 0,
            "attempt_count": 0,

            "percentage": None,

            "recent_percentage": None,

            "mastery_score": 0,

            "level": "not_started",

            "difficulty_performance": {
                "easy": {
                    "correct": 0,
                    "total": 0,
                    "percentage": None,
                },

                "medium": {
                    "correct": 0,
                    "total": 0,
                    "percentage": None,
                },

                "hard": {
                    "correct": 0,
                    "total": 0,
                    "percentage": None,
                },
            },
        }

    # -----------------------------------------------------
    # LIFETIME PERFORMANCE
    # -----------------------------------------------------

    lifetime_percentage = (
        correct / total
    ) * 100

    # -----------------------------------------------------
    # RECENT PERFORMANCE
    # -----------------------------------------------------

    recent_values = (
        attempt_percentages[
            -RECENT_ATTEMPT_WINDOW:
        ]
    )

    if recent_values:

        recent_percentage = (
            sum(recent_values)
            / len(recent_values)
        )

    else:

        recent_percentage = (
            lifetime_percentage
        )

    # -----------------------------------------------------
    # WEIGHTED MASTERY SCORE
    # -----------------------------------------------------

    mastery_score = (
        calculate_mastery_score(
            lifetime_percentage,
            recent_values,
        )
    )

    # -----------------------------------------------------
    # DIFFICULTY PERFORMANCE
    # -----------------------------------------------------

    difficulty_performance = (
        build_difficulty_performance(
            difficulty_stats
        )
    )

    # -----------------------------------------------------
    # FINAL ADAPTIVE LEVEL
    # -----------------------------------------------------

    level = (
        determine_adaptive_level(
            mastery_score,
            difficulty_performance,
        )
    )

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    return {
        "correct": (
            correct
        ),

        "total": (
            total
        ),

        "attempt_count": (
            attempt_count
        ),

        "percentage": round(
            lifetime_percentage,
            2,
        ),

        "recent_percentage": round(
            recent_percentage,
            2,
        ),

        "mastery_score": (
            mastery_score
        ),

        "level": (
            level
        ),

        "difficulty_performance": (
            difficulty_performance
        ),
    }


# =========================================================
# GET ONE TOPIC MASTERY
# =========================================================

def get_topic_mastery(
    student,
    topic,
):
    """
    Return mastery information for one topic.

    This function intentionally remains topic-based
    because it is also used by the adaptive engine
    and topic-locking logic.
    """

    attempts = (
        QuizAttempt.objects.filter(
            student=student,
            quiz__topic=topic,
        )
        .select_related(
            "quiz",
            "quiz__topic",
        )
        .prefetch_related(
            "answers__question"
        )
        .order_by(
            "attempted_at",
            "id",
        )
    )

    topic_stats = {
        "topic": topic,
        "correct": 0,
        "total": 0,
        "attempt_count": 0,
        "attempt_percentages": [],
        "difficulty_stats": (
            empty_difficulty_stats()
        ),
    }

    # -----------------------------------------------------
    # PROCESS ATTEMPTS
    # -----------------------------------------------------

    for attempt in attempts:

        attempt_correct = 0
        attempt_total = 0

        for answer in (
            attempt.answers.all()
        ):

            attempt_total += 1

            topic_stats[
                "total"
            ] += 1

            difficulty = (
                answer.question.difficulty
            )

            if difficulty not in {
                1,
                2,
                3,
            }:
                difficulty = 1

            topic_stats[
                "difficulty_stats"
            ][difficulty]["total"] += 1

            if answer.is_correct:

                attempt_correct += 1

                topic_stats[
                    "correct"
                ] += 1

                topic_stats[
                    "difficulty_stats"
                ][difficulty]["correct"] += 1

        if attempt_total > 0:

            attempt_percentage = (
                attempt_correct
                / attempt_total
            ) * 100

            topic_stats[
                "attempt_percentages"
            ].append(
                round(
                    attempt_percentage,
                    2,
                )
            )

        topic_stats[
            "attempt_count"
        ] += 1

    return build_mastery_data(
        topic_stats
    )


# =========================================================
# STUDENT TOPIC PERFORMANCE
# =========================================================

def build_student_topic_performance(
    student,
):
    """
    Return mastery information for topics that
    the student has attempted.

    Attempts from subjects that are no longer
    available to the student are excluded.
    """

    stats = (
        get_student_topic_stats(
            student
        )
    )

    results = []

    for topic_stats in (
        stats.values()
    ):

        topic = (
            topic_stats[
                "topic"
            ]
        )

        mastery = (
            build_mastery_data(
                topic_stats
            )
        )

        results.append(
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
                    topic.chapter
                    .subject.id
                ),

                "subject_name": (
                    topic.chapter
                    .subject.name
                ),

                **mastery,
            }
        )

    results.sort(
        key=lambda item: (
            item["subject_name"],
            item["chapter_id"],
            item["topic_id"],
        )
    )

    return results


# =========================================================
# NEXT TOPIC
# =========================================================

def get_next_topic(
    topic,
):
    """
    Return the next topic inside the same subject.

    First checks later topics in the current
    chapter. If none exist, moves to the next
    chapter in the same subject.
    """

    # -----------------------------------------------------
    # SAME CHAPTER
    # -----------------------------------------------------

    next_topic = (
        Topic.objects.filter(
            chapter=topic.chapter,
            id__gt=topic.id,
        )
        .order_by(
            "id"
        )
        .first()
    )

    if next_topic:
        return next_topic

    # -----------------------------------------------------
    # NEXT CHAPTER
    # -----------------------------------------------------

    return (
        Topic.objects.filter(
            chapter__subject=(
                topic.chapter.subject
            ),

            chapter__chapter_number__gt=(
                topic.chapter.chapter_number
            ),
        )
        .select_related(
            "chapter",
            "chapter__subject",
        )
        .order_by(
            "chapter__chapter_number",
            "id",
        )
        .first()
    )


# =========================================================
# RECOMMENDATION
# =========================================================

def create_recommendation(
    topic,
    mastery,
):

    level = (
        mastery[
            "level"
        ]
    )

    base = {
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

        "percentage": (
            mastery[
                "percentage"
            ]
        ),

        "recent_percentage": (
            mastery[
                "recent_percentage"
            ]
        ),

        "mastery_score": (
            mastery[
                "mastery_score"
            ]
        ),

        "level": (
            level
        ),

        "attempt_count": (
            mastery[
                "attempt_count"
            ]
        ),

        "difficulty_performance": (
            mastery[
                "difficulty_performance"
            ]
        ),
    }

    # -----------------------------------------------------
    # WEAK
    # -----------------------------------------------------

    if level == "weak":

        base.update(
            {
                "priority": 1,

                "recommendation_type": (
                    "revision"
                ),

                "title": (
                    f"Revise {topic.name}"
                ),

                "message": (
                    "Your mastery is currently low. "
                    "Review the lesson and try the "
                    "Easy quiz again."
                ),

                "recommended_difficulty": (
                    "easy"
                ),

                "difficulty_value": 1,

                "action": (
                    "review_lesson"
                ),

                "next_topic": None,
            }
        )

        return base

    # -----------------------------------------------------
    # DEVELOPING
    # -----------------------------------------------------

    if level == "developing":

        base.update(
            {
                "priority": 2,

                "recommendation_type": (
                    "practice"
                ),

                "title": (
                    f"Practice {topic.name}"
                ),

                "message": (
                    "You understand the basics. "
                    "Continue with Medium questions "
                    "to prove deeper understanding."
                ),

                "recommended_difficulty": (
                    "medium"
                ),

                "difficulty_value": 2,

                "action": (
                    "practice_topic"
                ),

                "next_topic": None,
            }
        )

        return base

    # -----------------------------------------------------
    # GOOD
    # -----------------------------------------------------

    if level == "good":

        base.update(
            {
                "priority": 3,

                "recommendation_type": (
                    "challenge"
                ),

                "title": (
                    f"Challenge yourself in "
                    f"{topic.name}"
                ),

                "message": (
                    "You have demonstrated "
                    "Medium-level understanding. "
                    "Attempt Hard questions to "
                    "prove mastery."
                ),

                "recommended_difficulty": (
                    "hard"
                ),

                "difficulty_value": 3,

                "action": (
                    "attempt_harder_questions"
                ),

                "next_topic": None,
            }
        )

        return base

    # -----------------------------------------------------
    # STRONG
    # -----------------------------------------------------

    next_topic = (
        get_next_topic(
            topic
        )
    )

    next_topic_data = None

    if next_topic:

        next_topic_data = {
            "id": (
                next_topic.id
            ),

            "name": (
                next_topic.name
            ),

            "chapter_id": (
                next_topic.chapter.id
            ),

            "chapter_name": (
                next_topic.chapter.name
            ),
        }

        message = (
            "Excellent work. You have mastered "
            f"this topic. Continue with "
            f"{next_topic.name}."
        )

    else:

        message = (
            "Excellent work. You have mastered "
            "this topic. Continue to the next "
            "available chapter."
        )

    base.update(
        {
            "priority": 4,

            "recommendation_type": (
                "mastered"
            ),

            "title": (
                f"{topic.name} mastered"
            ),

            "message": (
                message
            ),

            "recommended_difficulty": (
                "hard"
            ),

            "difficulty_value": 3,

            "action": (
                "move_forward"
            ),

            "next_topic": (
                next_topic_data
            ),
        }
    )

    return base


# =========================================================
# NOT STARTED RECOMMENDATION
# =========================================================

def create_not_started_recommendation(
    topic,
):

    return {
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

        "percentage": None,

        "recent_percentage": None,

        "mastery_score": 0,

        "level": (
            "not_started"
        ),

        "attempt_count": 0,

        "difficulty_performance": {
            "easy": {
                "correct": 0,
                "total": 0,
                "percentage": None,
            },

            "medium": {
                "correct": 0,
                "total": 0,
                "percentage": None,
            },

            "hard": {
                "correct": 0,
                "total": 0,
                "percentage": None,
            },
        },

        "priority": 2,

        "recommendation_type": (
            "start"
        ),

        "title": (
            f"Start {topic.name}"
        ),

        "message": (
            "Study the lesson first, review "
            "the examples and then attempt "
            "the introductory Easy quiz."
        ),

        "recommended_difficulty": (
            "easy"
        ),

        "difficulty_value": 1,

        "action": (
            "study_lesson"
        ),

        "next_topic": None,
    }


# =========================================================
# ALL RECOMMENDATIONS
# =========================================================

def build_student_recommendations(
    student,
):
    """
    Build recommendations only from subjects
    currently available to the student.

    This prevents recommendations from showing
    unrelated languages or optional subjects.
    """

    # -----------------------------------------------------
    # NO GRADE
    # -----------------------------------------------------

    if (
        student is None
        or not student.grade_id
    ):

        return {
            "summary": {
                "total_topics": 0,
                "not_started": 0,
                "weak": 0,
                "developing": 0,
                "good": 0,
                "strong": 0,
            },

            "recommendations": [],
        }

    # -----------------------------------------------------
    # STUDENT ALLOWED SUBJECTS
    # -----------------------------------------------------

    allowed_subject_ids = (
        get_allowed_subject_ids(
            student
        )
    )

    # -----------------------------------------------------
    # ALLOWED TOPICS ONLY
    # -----------------------------------------------------

    topics = list(
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

    # -----------------------------------------------------
    # EXISTING STUDENT PERFORMANCE
    # -----------------------------------------------------

    stats = (
        get_student_topic_stats(
            student
        )
    )

    summary = {
        "total_topics": (
            len(topics)
        ),

        "not_started": 0,

        "weak": 0,

        "developing": 0,

        "good": 0,

        "strong": 0,
    }

    recommendations = []

    # -----------------------------------------------------
    # PROCESS EVERY ALLOWED TOPIC
    # -----------------------------------------------------

    for topic in topics:

        topic_stats = (
            stats.get(
                topic.id
            )
        )

        # -------------------------------------------------
        # NOT STARTED
        # -------------------------------------------------

        if not topic_stats:

            summary[
                "not_started"
            ] += 1

            recommendations.append(
                create_not_started_recommendation(
                    topic
                )
            )

            continue

        # -------------------------------------------------
        # EXISTING MASTERY
        # -------------------------------------------------

        mastery = (
            build_mastery_data(
                topic_stats
            )
        )

        summary[
            mastery["level"]
        ] += 1

        recommendations.append(
            create_recommendation(
                topic,
                mastery,
            )
        )

    # -----------------------------------------------------
    # PRIORITY ORDER
    # -----------------------------------------------------

    recommendations.sort(
        key=lambda item: (
            item["priority"],
            item["mastery_score"],
            item["subject_name"],
            item["chapter_id"],
            item["topic_id"],
        )
    )

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return {
        "summary": (
            summary
        ),

        "recommendations": (
            recommendations
        ),
    }