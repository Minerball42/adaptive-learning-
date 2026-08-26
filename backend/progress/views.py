from django.db import transaction

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Student
from users.views import IsTeacherOrAdmin

from quizzes.models import Quiz, Question

from .models import QuizAttempt, Answer

from .services import (
    build_student_recommendations,
    build_student_topic_performance,
)

from .serializers import (
    ProgressErrorResponseSerializer,
    QuizAttemptResultSerializer,
    SubmitQuizRequestSerializer,
    SubmitQuizResponseSerializer,
    TopicPerformanceSerializer,
)


# ============================================================
# SUBMIT STANDARD QUIZ
# ============================================================

class SubmitQuizView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Progress"
        ],
        summary=(
            "Submit standard quiz"
        ),
        description=(
            "Submit answers for a standard quiz. "
            "All questions in the quiz must "
            "be answered."
        ),
        request=(
            SubmitQuizRequestSerializer
        ),
        responses={
            201: (
                SubmitQuizResponseSerializer
            ),
            400: (
                ProgressErrorResponseSerializer
            ),
            403: (
                ProgressErrorResponseSerializer
            ),
            404: (
                ProgressErrorResponseSerializer
            ),
        },
    )
    @transaction.atomic
    def post(self, request):

        quiz_id = request.data.get(
            "quiz"
        )

        answers = request.data.get(
            "answers"
        )

        # -----------------------------------------------------
        # QUIZ ID
        # -----------------------------------------------------

        if not quiz_id:

            return Response(
                {
                    "error": (
                        "Quiz is required."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # -----------------------------------------------------
        # ANSWERS
        # -----------------------------------------------------

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
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # -----------------------------------------------------
        # FIND QUIZ
        # -----------------------------------------------------

        try:

            quiz = (
                Quiz.objects
                .select_related(
                    "topic"
                )
                .get(
                    id=quiz_id
                )
            )

        except Quiz.DoesNotExist:

            return Response(
                {
                    "error": (
                        "Quiz not found."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        # -----------------------------------------------------
        # STUDENT
        # -----------------------------------------------------

        try:

            student = (
                request.user.student
            )

        except Student.DoesNotExist:

            return Response(
                {
                    "error": (
                        "Only students can "
                        "submit quizzes."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        # -----------------------------------------------------
        # QUESTIONS
        # -----------------------------------------------------

        questions = list(
            Question.objects.filter(
                quiz=quiz
            ).order_by(
                "id"
            )
        )

        if not questions:

            return Response(
                {
                    "error": (
                        "This quiz does not contain "
                        "any questions."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        question_map = {
            question.id: question
            for question
            in questions
        }

        answer_map = {}

        # -----------------------------------------------------
        # VALIDATE ANSWERS
        # -----------------------------------------------------

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

            if question_id is None:

                return Response(
                    {
                        "error": (
                            "Each answer must contain "
                            "a question ID."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
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
                            "Question ID must "
                            "be a number."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            if (
                question_id
                not in
                question_map
            ):

                return Response(
                    {
                        "error": (
                            f"Question {question_id} "
                            "does not belong to "
                            "this quiz."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            if (
                question_id
                in
                answer_map
            ):

                return Response(
                    {
                        "error": (
                            f"Question {question_id} "
                            "was answered more than once."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            if selected_answer is None:

                return Response(
                    {
                        "error": (
                            f"Answer is required for "
                            f"question {question_id}."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            selected_answer = (
                str(
                    selected_answer
                )
                .strip()
                .upper()
            )

            if selected_answer not in {
                "A",
                "B",
                "C",
                "D",
            }:

                return Response(
                    {
                        "error": (
                            "Answers must be one "
                            "of A, B, C or D."
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
        # ALL QUESTIONS MUST BE ANSWERED
        # -----------------------------------------------------

        if (
            len(answer_map)
            !=
            len(questions)
        ):

            return Response(
                {
                    "error": (
                        "All quiz questions must "
                        "be answered."
                    ),
                    "expected_answers": (
                        len(questions)
                    ),
                    "received_answers": (
                        len(answer_map)
                    ),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # -----------------------------------------------------
        # CREATE ATTEMPT
        # -----------------------------------------------------

        attempt = (
            QuizAttempt.objects.create(
                student=student,
                quiz=quiz,
                score=0,
                total_questions=(
                    len(questions)
                ),
            )
        )

        correct_count = 0

        answer_objects = []

        # -----------------------------------------------------
        # SERVER-SIDE SCORING
        # -----------------------------------------------------

        for question in questions:

            selected_answer = (
                answer_map[
                    question.id
                ]
            )

            is_correct = (
                selected_answer
                ==
                question.correct_answer
                .upper()
            )

            if is_correct:

                correct_count += 1

            answer_objects.append(
                Answer(
                    attempt=attempt,
                    question=question,
                    selected_answer=(
                        selected_answer
                    ),
                    is_correct=(
                        is_correct
                    ),
                )
            )

        Answer.objects.bulk_create(
            answer_objects
        )

        attempt.score = (
            correct_count
        )

        attempt.save(
            update_fields=[
                "score"
            ]
        )

        # Score/correct answers are intentionally
        # not returned here.

        return Response(
            {
                "message": (
                    "Quiz submitted successfully."
                ),
                "attempt_id": (
                    attempt.id
                ),
            },
            status=(
                status.HTTP_201_CREATED
            ),
        )


# ============================================================
# QUIZ ATTEMPT RESULTS
# ============================================================

class QuizAttemptResultsView(APIView):

    permission_classes = [
        IsTeacherOrAdmin
    ]

    @extend_schema(
        tags=[
            "Progress"
        ],
        summary=(
            "Get quiz attempt results"
        ),
        description=(
            "Return quiz attempts and detailed "
            "answers. This endpoint is restricted "
            "to teachers or administrators."
        ),
        responses={
            200: (
                QuizAttemptResultSerializer(
                    many=True
                )
            ),
            403: (
                ProgressErrorResponseSerializer
            ),
        },
    )
    def get(self, request):

        attempts = (
            QuizAttempt.objects
            .select_related(
                "student__user",
                "quiz",
                "quiz__topic",
            )
            .prefetch_related(
                "answers__question"
            )
            .order_by(
                "-attempted_at"
            )
        )

        results = []

        for attempt in attempts:

            answers = []

            for answer in (
                attempt.answers.all()
            ):

                answers.append(
                    {
                        "question": (
                            answer.question.id
                        ),

                        "question_text": (
                            answer.question
                            .question_text
                        ),

                        "student_answer": (
                            answer.selected_answer
                        ),

                        "correct_answer": (
                            answer.question
                            .correct_answer
                        ),

                        "correct": (
                            answer.is_correct
                        ),
                    }
                )

            percentage = (
                (
                    attempt.score
                    /
                    attempt.total_questions
                )
                * 100
                if attempt.total_questions > 0
                else 0
            )

            results.append(
                {
                    "id": (
                        attempt.id
                    ),

                    "student": (
                        attempt.student
                        .user.username
                    ),

                    "quiz": (
                        attempt.quiz.title
                    ),

                    "topic": (
                        attempt.quiz
                        .topic.name
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

                    "synced": (
                        attempt.synced
                    ),

                    "answers": (
                        answers
                    ),
                }
            )

        return Response(
            results,
            status=(
                status.HTTP_200_OK
            ),
        )


# ============================================================
# TEACHER TOPIC PERFORMANCE
# ============================================================

class TopicPerformanceView(APIView):

    permission_classes = [
        IsTeacherOrAdmin
    ]

    @extend_schema(
        tags=[
            "Progress"
        ],
        summary=(
            "Get topic performance analytics"
        ),
        description=(
            "Return topic-level performance "
            "statistics grouped by student. "
            "Restricted to teachers or admins."
        ),
        responses={
            200: (
                TopicPerformanceSerializer(
                    many=True
                )
            ),
            403: (
                ProgressErrorResponseSerializer
            ),
        },
    )
    def get(self, request):

        attempts = (
            QuizAttempt.objects
            .select_related(
                "student__user",
                "quiz__topic",
            )
            .prefetch_related(
                "answers"
            )
        )

        performance = {}

        # -----------------------------------------------------
        # BUILD RAW PERFORMANCE
        # -----------------------------------------------------

        for attempt in attempts:

            topic = (
                attempt.quiz.topic
            )

            topic_id = (
                topic.id
            )

            if (
                topic_id
                not in
                performance
            ):

                performance[
                    topic_id
                ] = {
                    "topic_id": (
                        topic.id
                    ),

                    "topic_name": (
                        topic.name
                    ),

                    "students": {},
                }

            student_id = (
                attempt.student.id
            )

            students = (
                performance[
                    topic_id
                ]["students"]
            )

            if (
                student_id
                not in
                students
            ):

                students[
                    student_id
                ] = {
                    "student_id": (
                        student_id
                    ),

                    "student_username": (
                        attempt.student
                        .user.username
                    ),

                    "correct": 0,

                    "total": 0,

                    "attempt_count": 0,
                }

            student_data = (
                students[
                    student_id
                ]
            )

            student_data[
                "attempt_count"
            ] += 1

            for answer in (
                attempt.answers.all()
            ):

                student_data[
                    "total"
                ] += 1

                if answer.is_correct:

                    student_data[
                        "correct"
                    ] += 1

        # -----------------------------------------------------
        # FINAL RESULT
        # -----------------------------------------------------

        results = []

        for topic_data in (
            performance.values()
        ):

            students = []

            for student_data in (
                topic_data[
                    "students"
                ].values()
            ):

                total = (
                    student_data[
                        "total"
                    ]
                )

                correct = (
                    student_data[
                        "correct"
                    ]
                )

                percentage = (
                    (
                        correct
                        /
                        total
                    )
                    * 100
                    if total > 0
                    else 0
                )

                students.append(
                    {
                        "student_id": (
                            student_data[
                                "student_id"
                            ]
                        ),

                        "student_username": (
                            student_data[
                                "student_username"
                            ]
                        ),

                        "correct": (
                            correct
                        ),

                        "total": (
                            total
                        ),

                        "attempt_count": (
                            student_data[
                                "attempt_count"
                            ]
                        ),

                        "percentage": round(
                            percentage,
                            2,
                        ),
                    }
                )

            results.append(
                {
                    "topic_id": (
                        topic_data[
                            "topic_id"
                        ]
                    ),

                    "topic_name": (
                        topic_data[
                            "topic_name"
                        ]
                    ),

                    "students": (
                        students
                    ),
                }
            )

        return Response(
            results,
            status=(
                status.HTTP_200_OK
            ),
        )


# ============================================================
# STUDENT TOPIC PERFORMANCE
# ============================================================

class MyTopicPerformanceView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Progress"
        ],
        summary=(
            "Get my topic performance"
        ),
        description=(
            "Return topic performance information "
            "for the authenticated student."
        ),
        responses={
            200: (
                OpenApiTypes.OBJECT
            ),
            403: (
                ProgressErrorResponseSerializer
            ),
        },
    )
    def get(self, request):

        try:

            student = (
                request.user.student
            )

        except Student.DoesNotExist:

            return Response(
                {
                    "error": (
                        "Only students can access "
                        "their performance."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        results = (
            build_student_topic_performance(
                student
            )
        )

        return Response(
            results,
            status=(
                status.HTTP_200_OK
            ),
        )


# ============================================================
# STUDENT RECOMMENDATIONS
# ============================================================

class MyRecommendationsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        tags=[
            "Progress"
        ],
        summary=(
            "Get learning recommendations"
        ),
        description=(
            "Return personalized learning "
            "recommendations based on the "
            "authenticated student's topic mastery."
        ),
        responses={
            200: (
                OpenApiTypes.OBJECT
            ),
            400: (
                ProgressErrorResponseSerializer
            ),
            403: (
                ProgressErrorResponseSerializer
            ),
        },
    )
    def get(self, request):

        try:

            student = (
                request.user.student
            )

        except Student.DoesNotExist:

            return Response(
                {
                    "error": (
                        "Only students can access "
                        "recommendations."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        if not student.grade:

            return Response(
                {
                    "error": (
                        "A grade must be assigned "
                        "before recommendations "
                        "can be generated."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        data = (
            build_student_recommendations(
                student
            )
        )

        return Response(
            data,
            status=(
                status.HTTP_200_OK
            ),
        )