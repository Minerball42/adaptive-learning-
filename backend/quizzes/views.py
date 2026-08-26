import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from drf_spectacular.types import (
    OpenApiTypes,
)

from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Topic
from progress.models import QuizAttempt, Answer
from progress.services import get_topic_mastery
from progress.learning_path import (
    is_topic_unlocked,
)
from users.models import Student

from .models import (
    Quiz,
    Question,
    AdaptiveQuizSession,
)

from .serializers import (
    AdaptiveQuizResponseSerializer,
    AdaptiveQuizSubmitRequestSerializer,
    AdaptiveQuizSubmitResponseSerializer,
    QuestionSerializer,
    QuizErrorResponseSerializer,
    QuizSerializer,
)

from .services import (
    get_difficulty_for_level,
    get_difficulty_name,
    select_adaptive_questions,
)


class QuizViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = QuizSerializer

    def get_queryset(self):
        queryset = (
            Quiz.objects
            .select_related(
                "topic",
                "topic__chapter",
                "topic__chapter__subject",
            )
            .all()
        )

        topic_id = (
            self.request
            .query_params
            .get("topic")
        )

        if topic_id:
            queryset = queryset.filter(
                topic_id=topic_id
            )

        return queryset


class QuestionViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset = (
            Question.objects
            .select_related(
                "quiz",
                "quiz__topic",
            )
            .all()
        )

        quiz_id = (
            self.request
            .query_params
            .get("quiz")
        )

        if quiz_id:
            queryset = queryset.filter(
                quiz_id=quiz_id
            )

        difficulty = (
            self.request
            .query_params
            .get("difficulty")
        )

        if difficulty:
            queryset = queryset.filter(
                difficulty=difficulty
            )

        return queryset


class AdaptiveQuizView(APIView):
    """
    Create an adaptive quiz session.

    GET /api/quizzes/adaptive/?topic=1
    """

    permission_classes = [
        IsAuthenticated
    ]

    QUESTION_LIMIT = 3
    SESSION_MINUTES = 30
    @extend_schema(
        tags=[
            "Adaptive Quiz"
        ],

        summary=(
            "Create adaptive quiz session"
        ),

        description=(
            "Create a new adaptive quiz session "
            "for the authenticated student. "
            "Question difficulty is selected "
            "according to the student's current "
            "topic mastery."
        ),

        parameters=[
            OpenApiParameter(
                name="topic",

                type=OpenApiTypes.INT,

                location=(
                    OpenApiParameter.QUERY
                ),

                required=True,

                description=(
                    "ID of the topic for which "
                    "an adaptive quiz should "
                    "be generated."
                ),
            ),
        ],

        responses={
            200: (
                AdaptiveQuizResponseSerializer
            ),

            400: (
                QuizErrorResponseSerializer
            ),

            403: (
                QuizErrorResponseSerializer
            ),

            404: (
                QuizErrorResponseSerializer
            ),
        },
    )

    def get(self, request):

        # -----------------------------------------------------
        # STUDENT
        # -----------------------------------------------------

        try:
            student = request.user.student

        except Student.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Only students can access "
                        "adaptive quizzes."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not student.grade:
            return Response(
                {
                    "error": (
                        "The student must have "
                        "a grade assigned."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------
        # TOPIC ID
        # -----------------------------------------------------

        topic_id = (
            request.query_params
            .get("topic")
        )

        if not topic_id:
            return Response(
                {
                    "error": (
                        "Topic ID is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            topic_id = int(topic_id)

        except (
            TypeError,
            ValueError,
        ):
            return Response(
                {
                    "error": (
                        "Topic ID must be "
                        "a valid number."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------
        # TOPIC
        # -----------------------------------------------------

        try:
            topic = (
                Topic.objects
                .select_related(
                    "chapter",
                    "chapter__subject",
                    "chapter__subject__grade",
                )
                .get(
                    id=topic_id,
                    chapter__subject__grade=(
                        student.grade
                    ),
                )
            )

        except Topic.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Topic not found for this "
                        "student's grade."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )
                # -----------------------------------------------------
        # TOPIC UNLOCK CHECK
        # -----------------------------------------------------

        unlock = is_topic_unlocked(
            student,
            topic,
        )

        if not unlock["unlocked"]:

            return Response(
                {
                    "error": (
                        "This topic is locked."
                    ),

                    "topic": {
                        "id": topic.id,
                        "name": topic.name,
                    },

                    "previous_topic": (
                        unlock[
                            "previous_topic"
                        ]
                    ),

                    "message": (
                        "Master the previous topic "
                        "before starting this one."
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        # -----------------------------------------------------
        # QUIZ
        # -----------------------------------------------------

        quiz = (
            Quiz.objects
            .filter(topic=topic)
            .order_by("id")
            .first()
        )

        if not quiz:
            return Response(
                {
                    "error": (
                        "No quiz is available "
                        "for this topic."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # -----------------------------------------------------
        # MASTERY
        # -----------------------------------------------------

        mastery = get_topic_mastery(
            student,
            topic,
        )

        target_difficulty = (
            get_difficulty_for_level(
                mastery["level"]
            )
        )

        # -----------------------------------------------------
        # SELECT QUESTIONS
        # -----------------------------------------------------

        selection = (
            select_adaptive_questions(
                quiz=quiz,
                target_difficulty=(
                    target_difficulty
                ),
                limit=self.QUESTION_LIMIT,
            )
        )

        questions = (
            selection["questions"]
        )

        if not questions:
            return Response(
                {
                    "error": (
                        "No questions are available "
                        "for this quiz."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # -----------------------------------------------------
        # CANCEL OLD ACTIVE SESSION FOR THIS QUIZ
        # -----------------------------------------------------

        AdaptiveQuizSession.objects.filter(
            student=student,
            quiz=quiz,
            status="active",
        ).update(
            status="cancelled"
        )

        # -----------------------------------------------------
        # CREATE SESSION
        # -----------------------------------------------------

        expires_at = (
            timezone.now()
            + timedelta(
                minutes=self.SESSION_MINUTES
            )
        )

        session = (
            AdaptiveQuizSession.objects.create(
                student=student,
                quiz=quiz,
                target_difficulty=(
                    target_difficulty
                ),
                mastery_score_before=(
                    mastery["mastery_score"]
                ),
                mastery_level_before=(
                    mastery["level"]
                ),
                expires_at=expires_at,
            )
        )

        session.questions.set(
            questions
        )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return Response(
            {
                "session": {
                    "id": str(session.id),
                    "status": session.status,
                    "created_at": (
                        session.created_at
                    ),
                    "expires_at": (
                        session.expires_at
                    ),
                },

                "topic": {
                    "id": topic.id,
                    "name": topic.name,
                    "chapter": (
                        topic.chapter.name
                    ),
                    "subject": (
                        topic.chapter
                        .subject.name
                    ),
                },

                "mastery": mastery,

                "adaptive_selection": {
                    "difficulty_value": (
                        target_difficulty
                    ),
                    "difficulty": (
                        get_difficulty_name(
                            target_difficulty
                        )
                    ),
                    "question_limit": (
                        self.QUESTION_LIMIT
                    ),
                    "fallback_used": (
                        selection[
                            "fallback_used"
                        ]
                    ),
                    "actual_difficulties": (
                        selection[
                            "actual_difficulties"
                        ]
                    ),
                },

                "quiz": {
                    "id": quiz.id,
                    "title": quiz.title,
                    "description": (
                        quiz.description
                    ),
                },

                "questions": (
                    QuestionSerializer(
                        questions,
                        many=True,
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )


class AdaptiveQuizSubmitView(APIView):
    """
    Submit a previously created adaptive
    quiz session.

    POST /api/quizzes/adaptive/submit/
    """

    permission_classes = [
        IsAuthenticated
    ]
    
    @extend_schema(
        tags=[
            "Adaptive Quiz"
        ],

        summary=(
            "Submit adaptive quiz session"
        ),

        description=(
            "Submit answers for an active "
            "adaptive quiz session. "
            "The server validates the exact "
            "questions assigned to the session, "
            "scores the attempt, recalculates "
            "mastery, and selects the next "
            "adaptive difficulty."
        ),

        request=(
            AdaptiveQuizSubmitRequestSerializer
        ),

        responses={
            201: (
                AdaptiveQuizSubmitResponseSerializer
            ),

            400: (
                QuizErrorResponseSerializer
            ),

            403: (
                QuizErrorResponseSerializer
            ),

            404: (
                QuizErrorResponseSerializer
            ),
        },
    )
    @transaction.atomic
    def post(self, request):

    

        # -----------------------------------------------------
        # STUDENT
        # -----------------------------------------------------

        try:
            student = request.user.student

        except Student.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Only students can submit "
                        "adaptive quizzes."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # -----------------------------------------------------
        # INPUT
        # -----------------------------------------------------

        session_id = request.data.get(
            "session_id"
        )

        answers = request.data.get(
            "answers"
        )

        if not session_id:
            return Response(
                {
                    "error": (
                        "session_id is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(
            answers,
            list,
        ):
            return Response(
                {
                    "error": (
                        "Answers must be provided "
                        "as a list."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------
        # VALIDATE UUID
        # -----------------------------------------------------

        try:
            session_uuid = uuid.UUID(
                str(session_id)
            )

        except (
            ValueError,
            TypeError,
            AttributeError,
        ):
            return Response(
                {
                    "error": (
                        "Invalid adaptive quiz "
                        "session ID."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------
        # LOAD + LOCK SESSION
        # -----------------------------------------------------

        try:
            session = (
                AdaptiveQuizSession.objects
                .select_for_update()
                .select_related(
                    "student",
                    "quiz",
                    "quiz__topic",
                    "quiz__topic__chapter",
                    "quiz__topic__chapter__subject",
                )
                .prefetch_related(
                    "questions"
                )
                .get(
                    id=session_uuid,
                    student=student,
                )
            )

        except AdaptiveQuizSession.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Adaptive quiz session "
                        "was not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # -----------------------------------------------------
        # SESSION STATUS
        # -----------------------------------------------------

        if session.status != "active":
            return Response(
                {
                    "error": (
                        "This adaptive quiz session "
                        "is no longer active."
                    ),
                    "session_status": (
                        session.status
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------
        # EXPIRATION
        # -----------------------------------------------------

        if timezone.now() > session.expires_at:

            session.status = "expired"

            session.save(
                update_fields=[
                    "status"
                ]
            )

            return Response(
                {
                    "error": (
                        "This adaptive quiz "
                        "session has expired. "
                        "Request a new quiz."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------
        # ASSIGNED QUESTIONS
        # -----------------------------------------------------

        selected_questions = list(
            session.questions.all()
            .order_by("id")
        )

        if not selected_questions:
            return Response(
                {
                    "error": (
                        "No questions are assigned "
                        "to this session."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        expected_question_ids = [
            question.id
            for question
            in selected_questions
        ]

        question_map = {
            question.id: question
            for question
            in selected_questions
        }

        # -----------------------------------------------------
        # VALIDATE ANSWERS
        # -----------------------------------------------------

        answer_map = {}

        for item in answers:

            if not isinstance(
                item,
                dict,
            ):
                return Response(
                    {
                        "error": (
                            "Each answer must be "
                            "an object."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            question_id = item.get(
                "question"
            )

            selected_answer = item.get(
                "answer"
            )

            try:
                question_id = int(
                    question_id
                )

            except (
                TypeError,
                ValueError,
            ):
                return Response(
                    {
                        "error": (
                            "Every question ID must "
                            "be a valid number."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            if (
                question_id
                in answer_map
            ):
                return Response(
                    {
                        "error": (
                            f"Question {question_id} "
                            "was answered more "
                            "than once."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            selected_answer = str(
                selected_answer
            ).strip().upper()

            if selected_answer not in {
                "A",
                "B",
                "C",
                "D",
            }:
                return Response(
                    {
                        "error": (
                            "Answers must be "
                            "A, B, C or D."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            answer_map[
                question_id
            ] = selected_answer

        # -----------------------------------------------------
        # EXACT QUESTION MATCH
        # -----------------------------------------------------

        submitted_ids = sorted(
            answer_map.keys()
        )

        expected_ids = sorted(
            expected_question_ids
        )

        if submitted_ids != expected_ids:
            return Response(
                {
                    "error": (
                        "Submitted questions do not "
                        "match the questions assigned "
                        "to this adaptive quiz session."
                    ),
                    "expected_question_ids": (
                        expected_ids
                    ),
                    "submitted_question_ids": (
                        submitted_ids
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------
        # MASTERY BEFORE
        # -----------------------------------------------------

        topic = session.quiz.topic

        mastery_before = (
            get_topic_mastery(
                student,
                topic,
            )
        )

        # -----------------------------------------------------
        # CREATE QUIZ ATTEMPT
        # -----------------------------------------------------

        attempt = (
            QuizAttempt.objects.create(
                student=student,
                quiz=session.quiz,
                score=0,
                total_questions=len(
                    selected_questions
                ),
            )
        )

        score = 0
        answer_objects = []

        for question in (
            selected_questions
        ):

            selected_answer = (
                answer_map[
                    question.id
                ]
            )

            is_correct = (
                selected_answer
                == question
                .correct_answer
                .strip()
                .upper()
            )

            if is_correct:
                score += 1

            answer_objects.append(
                Answer(
                    attempt=attempt,
                    question=question,
                    selected_answer=(
                        selected_answer
                    ),
                    is_correct=is_correct,
                )
            )

        Answer.objects.bulk_create(
            answer_objects
        )

        attempt.score = score

        attempt.save(
            update_fields=[
                "score"
            ]
        )

        # -----------------------------------------------------
        # COMPLETE SESSION
        # -----------------------------------------------------

        session.status = "completed"

        session.submitted_at = (
            timezone.now()
        )

        session.save(
            update_fields=[
                "status",
                "submitted_at",
            ]
        )

        # -----------------------------------------------------
        # MASTERY AFTER
        # -----------------------------------------------------

        mastery_after = (
            get_topic_mastery(
                student,
                topic,
            )
        )

        next_difficulty_value = (
            get_difficulty_for_level(
                mastery_after["level"]
            )
        )

        attempt_percentage = (
            (
                score
                / len(
                    selected_questions
                )
            )
            * 100
        )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return Response(
            {
                "message": (
                    "Adaptive quiz session "
                    "submitted successfully."
                ),

                "session": {
                    "id": str(
                        session.id
                    ),
                    "status": (
                        session.status
                    ),
                    "submitted_at": (
                        session.submitted_at
                    ),
                },

                "attempt_id": (
                    attempt.id
                ),

                "topic": {
                    "id": topic.id,
                    "name": topic.name,
                },

                "quiz": {
                    "id": (
                        session.quiz.id
                    ),
                    "title": (
                        session.quiz.title
                    ),
                },

                "attempt": {
                    "score": score,
                    "total_questions": (
                        len(
                            selected_questions
                        )
                    ),
                    "percentage": round(
                        attempt_percentage,
                        2,
                    ),
                },

                "mastery_before": (
                    mastery_before
                ),

                "mastery_after": (
                    mastery_after
                ),

                "next_adaptive_difficulty": {
                    "value": (
                        next_difficulty_value
                    ),
                    "name": (
                        get_difficulty_name(
                            next_difficulty_value
                        )
                    ),
                },
            },
            status=status.HTTP_201_CREATED,
        )