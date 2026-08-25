import uuid

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from courses.models import Topic
from progress.models import (
    Answer,
    QuizAttempt,
)
from progress.services import (
    get_topic_mastery,
)
from quizzes.models import (
    Question,
    Quiz,
)

from .models import OfflineSyncRecord


def normalize_answer(value):
    """
    Convert submitted answer to A/B/C/D.
    """

    if not isinstance(value, str):
        return None

    answer = value.strip().upper()

    if answer not in {
        "A",
        "B",
        "C",
        "D",
    }:
        return None

    return answer


def parse_client_datetime(value):
    """
    Parse optional ISO client datetime.
    """

    if not value:
        return None

    if not isinstance(value, str):
        return None

    parsed = parse_datetime(
        value
    )

    if parsed is None:
        return None

    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(
            parsed
        )

    return parsed


def build_sync_result(
    sync_record,
    already_synced=False,
):
    """
    Build response for an existing or
    newly synchronized attempt.
    """

    attempt = (
        sync_record.quiz_attempt
    )

    result = {
        "sync_id": str(
            sync_record.id
        ),

        "client_attempt_id": str(
            sync_record.client_attempt_id
        ),

        "status": (
            sync_record.status
        ),

        "already_synced": (
            already_synced
        ),

        "device_id": (
            sync_record.device_id
        ),

        "received_at": (
            sync_record.received_at
        ),

        "synced_at": (
            sync_record.synced_at
        ),
    }

    if attempt:

        topic = attempt.quiz.topic

        if attempt.total_questions > 0:

            percentage = (
                attempt.score
                /
                attempt.total_questions
            ) * 100

        else:
            percentage = 0

        mastery = get_topic_mastery(
            sync_record.student,
            topic,
        )

        result["attempt"] = {
            "attempt_id": (
                attempt.id
            ),

            "quiz_id": (
                attempt.quiz.id
            ),

            "topic_id": (
                topic.id
            ),

            "topic_name": (
                topic.name
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
        }

        result["mastery"] = (
            mastery
        )

    return result


def sync_offline_quiz_attempt(
    student,
    payload,
):
    """
    Validate and synchronize one quiz attempt.

    Returns:
        data, http_status
    """

    # ---------------------------------------------------------
    # CLIENT ATTEMPT ID
    # ---------------------------------------------------------

    raw_client_attempt_id = (
        payload.get(
            "client_attempt_id"
        )
    )

    if not raw_client_attempt_id:

        return (
            {
                "error": (
                    "client_attempt_id "
                    "is required."
                )
            },
            400,
        )

    try:

        client_attempt_id = uuid.UUID(
            str(
                raw_client_attempt_id
            )
        )

    except (
        ValueError,
        TypeError,
        AttributeError,
    ):

        return (
            {
                "error": (
                    "client_attempt_id "
                    "must be a valid UUID."
                )
            },
            400,
        )

    # ---------------------------------------------------------
    # QUIZ ID
    # ---------------------------------------------------------

    raw_quiz_id = payload.get(
        "quiz_id"
    )

    try:

        quiz_id = int(
            raw_quiz_id
        )

    except (
        TypeError,
        ValueError,
    ):

        return (
            {
                "error": (
                    "quiz_id must be "
                    "a valid number."
                )
            },
            400,
        )

    # ---------------------------------------------------------
    # ANSWERS
    # ---------------------------------------------------------

    submitted_answers = payload.get(
        "answers"
    )

    if not isinstance(
        submitted_answers,
        list,
    ):

        return (
            {
                "error": (
                    "answers must be "
                    "a list."
                )
            },
            400,
        )

    if len(
        submitted_answers
    ) == 0:

        return (
            {
                "error": (
                    "At least one answer "
                    "is required."
                )
            },
            400,
        )

    # ---------------------------------------------------------
    # DEVICE
    # ---------------------------------------------------------

    device_id = payload.get(
        "device_id",
        "",
    )

    if device_id is None:
        device_id = ""

    device_id = str(
        device_id
    ).strip()

    if len(device_id) > 200:

        return (
            {
                "error": (
                    "device_id cannot exceed "
                    "200 characters."
                )
            },
            400,
        )

    # ---------------------------------------------------------
    # CLIENT CREATED TIME
    # ---------------------------------------------------------

    raw_client_created_at = (
        payload.get(
            "client_created_at"
        )
    )

    client_created_at = (
        parse_client_datetime(
            raw_client_created_at
        )
    )

    if (
        raw_client_created_at
        and
        client_created_at is None
    ):

        return (
            {
                "error": (
                    "client_created_at must "
                    "be a valid ISO datetime."
                )
            },
            400,
        )

    # ---------------------------------------------------------
    # TRANSACTION
    # ---------------------------------------------------------

    with transaction.atomic():

        existing = (
            OfflineSyncRecord.objects
            .select_for_update()
            .filter(
                student=student,
                client_attempt_id=(
                    client_attempt_id
                ),
            )
            .first()
        )

        # -----------------------------------------------------
        # IDEMPOTENT RETRY
        # -----------------------------------------------------

        if (
            existing
            and
            existing.status == "synced"
            and
            existing.quiz_attempt_id
        ):

            return (
                build_sync_result(
                    existing,
                    already_synced=True,
                ),
                200,
            )

        # -----------------------------------------------------
        # CREATE OR REUSE SYNC RECORD
        # -----------------------------------------------------

        if existing:

            sync_record = existing

            sync_record.status = (
                "pending"
            )

            sync_record.error_message = ""

            sync_record.device_id = (
                device_id
            )

            sync_record.client_created_at = (
                client_created_at
            )

            sync_record.save(
                update_fields=[
                    "status",
                    "error_message",
                    "device_id",
                    "client_created_at",
                ]
            )

        else:

            sync_record = (
                OfflineSyncRecord.objects.create(
                    student=student,

                    client_attempt_id=(
                        client_attempt_id
                    ),

                    device_id=device_id,

                    client_created_at=(
                        client_created_at
                    ),

                    status="pending",
                )
            )

        # -----------------------------------------------------
        # FIND QUIZ
        # -----------------------------------------------------

        quiz = (
            Quiz.objects
            .select_related(
                "topic",
                "topic__chapter",
                "topic__chapter__subject",
                "topic__chapter__subject__grade",
            )
            .filter(
                id=quiz_id
            )
            .first()
        )

        if quiz is None:

            sync_record.status = (
                "failed"
            )

            sync_record.error_message = (
                "Quiz not found."
            )

            sync_record.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

            return (
                {
                    "error": (
                        "Quiz not found."
                    ),

                    "sync_id": str(
                        sync_record.id
                    ),

                    "status": "failed",
                },
                404,
            )

        # -----------------------------------------------------
        # STUDENT GRADE CHECK
        # -----------------------------------------------------

        if not student.grade:

            sync_record.status = (
                "failed"
            )

            sync_record.error_message = (
                "Student does not have "
                "a grade assigned."
            )

            sync_record.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

            return (
                {
                    "error": (
                        "Student must have "
                        "a grade assigned."
                    ),

                    "sync_id": str(
                        sync_record.id
                    ),

                    "status": "failed",
                },
                400,
            )

        quiz_grade = (
            quiz.topic.chapter
            .subject.grade
        )

        if (
            quiz_grade.id
            !=
            student.grade.id
        ):

            sync_record.status = (
                "failed"
            )

            sync_record.error_message = (
                "Quiz does not belong to "
                "the student's grade."
            )

            sync_record.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

            return (
                {
                    "error": (
                        "You cannot submit "
                        "this quiz."
                    ),

                    "sync_id": str(
                        sync_record.id
                    ),

                    "status": "failed",
                },
                403,
            )

        # -----------------------------------------------------
        # VALIDATE QUESTION PAYLOAD
        # -----------------------------------------------------

        answer_map = {}

        for item in submitted_answers:

            if not isinstance(
                item,
                dict,
            ):

                return (
                    {
                        "error": (
                            "Every answer must "
                            "be an object."
                        )
                    },
                    400,
                )

            raw_question_id = (
                item.get(
                    "question"
                )
            )

            try:

                question_id = int(
                    raw_question_id
                )

            except (
                TypeError,
                ValueError,
            ):

                return (
                    {
                        "error": (
                            "Every question ID "
                            "must be a valid number."
                        )
                    },
                    400,
                )

            if (
                question_id
                in answer_map
            ):

                return (
                    {
                        "error": (
                            "Duplicate question IDs "
                            "are not allowed."
                        )
                    },
                    400,
                )

            answer = normalize_answer(
                item.get(
                    "answer"
                )
            )

            if answer is None:

                return (
                    {
                        "error": (
                            "Answers must be "
                            "A, B, C or D."
                        )
                    },
                    400,
                )

            answer_map[
                question_id
            ] = answer

        # -----------------------------------------------------
        # LOAD QUESTIONS
        # -----------------------------------------------------

        questions = list(
            Question.objects.filter(
                quiz=quiz,
                id__in=answer_map.keys(),
            ).order_by(
                "id"
            )
        )

        if (
            len(questions)
            !=
            len(answer_map)
        ):

            sync_record.status = (
                "failed"
            )

            sync_record.error_message = (
                "One or more questions do "
                "not belong to this quiz."
            )

            sync_record.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

            return (
                {
                    "error": (
                        "One or more questions "
                        "do not belong to "
                        "this quiz."
                    ),

                    "sync_id": str(
                        sync_record.id
                    ),

                    "status": "failed",
                },
                400,
            )

        # -----------------------------------------------------
        # SERVER-SIDE SCORING
        # -----------------------------------------------------

        score = 0

        answer_objects = []

        for question in questions:

            selected_answer = (
                answer_map[
                    question.id
                ]
            )

            correct_answer = (
                question.correct_answer
                .strip()
                .upper()
            )

            is_correct = (
                selected_answer
                ==
                correct_answer
            )

            if is_correct:
                score += 1

            answer_objects.append(
                {
                    "question": (
                        question
                    ),

                    "selected_answer": (
                        selected_answer
                    ),

                    "is_correct": (
                        is_correct
                    ),
                }
            )

        # -----------------------------------------------------
        # CREATE QUIZ ATTEMPT
        # -----------------------------------------------------

        attempt = (
            QuizAttempt.objects.create(
                student=student,
                quiz=quiz,
                score=score,
                total_questions=(
                    len(questions)
                ),
            )
        )

        # -----------------------------------------------------
        # CREATE ANSWERS
        # -----------------------------------------------------

        Answer.objects.bulk_create(
            [
                Answer(
                    attempt=attempt,

                    question=item[
                        "question"
                    ],

                    selected_answer=item[
                        "selected_answer"
                    ],

                    is_correct=item[
                        "is_correct"
                    ],
                )

                for item
                in answer_objects
            ]
        )

        # -----------------------------------------------------
        # COMPLETE SYNC RECORD
        # -----------------------------------------------------

        sync_record.quiz_attempt = (
            attempt
        )

        sync_record.status = (
            "synced"
        )

        sync_record.synced_at = (
            timezone.now()
        )

        sync_record.error_message = ""

        sync_record.save(
            update_fields=[
                "quiz_attempt",
                "status",
                "synced_at",
                "error_message",
            ]
        )

        # -----------------------------------------------------
        # FINAL RESULT
        # -----------------------------------------------------

        return (
            build_sync_result(
                sync_record,
                already_synced=False,
            ),
            201,
        )