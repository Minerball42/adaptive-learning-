from progress.dashboard import build_dashboard
from progress.learning_path import (
    build_learning_path,
    get_ordered_topics,
)
from progress.models import QuizAttempt
from progress.services import get_topic_mastery

from users.models import Student


def get_teacher_students(teacher):
    """
    Return students belonging to the
    same school as the teacher.
    """

    return (
        Student.objects.filter(
            school=teacher.school
        )
        .select_related(
            "user",
            "grade",
        )
        .order_by(
            "user__username"
        )
    )


def get_teacher_student(
    teacher,
    student_id,
):
    """
    Return one student only if the student
    belongs to the teacher's school.
    """

    return (
        Student.objects.filter(
            id=student_id,
            school=teacher.school,
        )
        .select_related(
            "user",
            "grade",
        )
        .first()
    )


def build_student_summary(student):
    """
    Build compact progress information
    for a student.
    """

    learning_path = build_learning_path(
        student
    )

    summary = learning_path.get(
        "summary",
        {},
    )

    attempts = QuizAttempt.objects.filter(
        student=student
    )

    attempt_count = attempts.count()

    total_questions = 0
    total_correct = 0

    for attempt in attempts:

        total_questions += (
            attempt.total_questions
        )

        total_correct += (
            attempt.score
        )

    if total_questions > 0:

        quiz_accuracy = (
            total_correct
            / total_questions
        ) * 100

    else:

        quiz_accuracy = 0

    grade_name = None

    if student.grade:

        grade_name = (
            student.grade.name
        )

    return {
        "student_id": student.id,

        "username": (
            student.user.username
        ),

        "email": (
            student.user.email
        ),

        "grade": grade_name,

        "school": (
            student.school
        ),

        "preferred_language": (
            student.preferred_language
        ),

        "total_topics": (
            summary.get(
                "total_topics",
                0,
            )
        ),

        "completed_topics": (
            summary.get(
                "completed",
                0,
            )
        ),

        "available_topics": (
            summary.get(
                "available",
                0,
            )
        ),

        "locked_topics": (
            summary.get(
                "locked",
                0,
            )
        ),

        "completion_percentage": (
            summary.get(
                "completion_percentage",
                0,
            )
        ),

        "quiz_attempts": (
            attempt_count
        ),

        "quiz_accuracy": round(
            quiz_accuracy,
            2,
        ),
    }


def build_teacher_dashboard(teacher):
    """
    Build overall teacher dashboard statistics.
    """

    students = list(
        get_teacher_students(
            teacher
        )
    )

    student_summaries = []

    total_completion = 0
    total_accuracy = 0

    students_with_attempts = 0
    completed_students = 0
    students_needing_help = 0

    for student in students:

        data = build_student_summary(
            student
        )

        student_summaries.append(
            data
        )

        total_completion += (
            data["completion_percentage"]
        )

        if data["quiz_attempts"] > 0:

            students_with_attempts += 1

            total_accuracy += (
                data["quiz_accuracy"]
            )

        if (
            data["total_topics"] > 0
            and
            data["completed_topics"]
            ==
            data["total_topics"]
        ):

            completed_students += 1

        if (
            data["quiz_attempts"] > 0
            and
            data["quiz_accuracy"] < 50
        ):

            students_needing_help += 1

    total_students = len(
        student_summaries
    )

    if total_students > 0:

        average_completion = (
            total_completion
            / total_students
        )

    else:

        average_completion = 0

    if students_with_attempts > 0:

        average_quiz_accuracy = (
            total_accuracy
            / students_with_attempts
        )

    else:

        average_quiz_accuracy = 0

    total_attempts = (
        QuizAttempt.objects.filter(
            student__school=teacher.school
        ).count()
    )

    return {
        "teacher": {
            "teacher_id": teacher.id,
            "username": teacher.user.username,
            "email": teacher.user.email,
            "school": teacher.school,
        },

        "overview": {
            "total_students": (
                total_students
            ),

            "active_students": (
                students_with_attempts
            ),

            "completed_students": (
                completed_students
            ),

            "students_needing_help": (
                students_needing_help
            ),

            "total_quiz_attempts": (
                total_attempts
            ),

            "average_completion_percentage": round(
                average_completion,
                2,
            ),

            "average_quiz_accuracy": round(
                average_quiz_accuracy,
                2,
            ),
        },

        "students": (
            student_summaries
        ),
    }


def build_teacher_student_progress(
    student
):
    """
    Full dashboard/progress information
    for one student.
    """

    dashboard = build_dashboard(
        student
    )

    dashboard["student"][
        "student_id"
    ] = student.id

    return dashboard


def build_teacher_weak_topics(
    teacher
):
    """
    Find weak/developing topics for students
    in the teacher's school.
    """

    students = get_teacher_students(
        teacher
    )

    topic_data = {}

    for student in students:

        if not student.grade:
            continue

        topics = get_ordered_topics(
            student
        )

        for topic in topics:

            mastery = get_topic_mastery(
                student,
                topic,
            )

            level = mastery[
                "level"
            ]

            if level not in (
                "weak",
                "developing",
            ):
                continue

            if topic.id not in topic_data:

                topic_data[topic.id] = {
                    "topic_id": topic.id,

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

                    "weak_students": 0,

                    "developing_students": 0,

                    "student_count": 0,

                    "mastery_total": 0,

                    "attempt_count": 0,

                    "students": [],
                }

            entry = topic_data[
                topic.id
            ]

            entry[
                "student_count"
            ] += 1

            entry[
                "mastery_total"
            ] += mastery[
                "mastery_score"
            ]

            entry[
                "attempt_count"
            ] += mastery[
                "attempt_count"
            ]

            if level == "weak":

                entry[
                    "weak_students"
                ] += 1

            if level == "developing":

                entry[
                    "developing_students"
                ] += 1

            entry["students"].append(
                {
                    "student_id": (
                        student.id
                    ),

                    "username": (
                        student.user.username
                    ),

                    "level": level,

                    "mastery_score": (
                        mastery[
                            "mastery_score"
                        ]
                    ),

                    "attempt_count": (
                        mastery[
                            "attempt_count"
                        ]
                    ),
                }
            )

    results = []

    for entry in topic_data.values():

        if entry[
            "student_count"
        ] > 0:

            average_mastery = (
                entry[
                    "mastery_total"
                ]
                /
                entry[
                    "student_count"
                ]
            )

        else:

            average_mastery = 0

        entry[
            "average_mastery"
        ] = round(
            average_mastery,
            2,
        )

        del entry[
            "mastery_total"
        ]

        results.append(
            entry
        )

    results.sort(
        key=lambda item: (
            item[
                "average_mastery"
            ],
            -item[
                "student_count"
            ],
        )
    )

    return {
        "count": len(results),

        "weak_topics": results,
    }


def build_teacher_recent_attempts(
    teacher,
    limit=20,
):
    """
    Return recent quiz attempts from students
    in the teacher's school.
    """

    attempts = (
        QuizAttempt.objects.filter(
            student__school=teacher.school
        )
        .select_related(
            "student",
            "student__user",
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

        topic = attempt.quiz.topic
        chapter = topic.chapter
        subject = chapter.subject

        results.append(
            {
                "attempt_id": (
                    attempt.id
                ),

                "student_id": (
                    attempt.student.id
                ),

                "username": (
                    attempt.student.user.username
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

    return {
        "count": len(results),

        "attempts": results,
    }