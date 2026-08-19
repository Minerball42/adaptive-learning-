from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.views import IsTeacherOrAdmin
from quizzes.models import Quiz, Question
from .models import QuizAttempt, Answer


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        quiz_id = request.data.get("quiz")
        answers = request.data.get("answers")

        if not quiz_id:
            return Response(
                {"error": "Quiz is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(answers, list):
            return Response(
                {"error": "Answers must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response(
                {"error": "Quiz not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Make sure the logged-in user is a student
        try:
            student = request.user.student
        except Exception:
            return Response(
                {"error": "Only students can submit quizzes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        questions = Question.objects.filter(quiz=quiz)

        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=0,
            total_questions=questions.count(),
        )

        correct_count = 0

        for item in answers:
            question_id = item.get("question")
            selected_answer = item.get("answer")

            if not question_id or not selected_answer:
                continue

            try:
                question = questions.get(id=question_id)
            except Question.DoesNotExist:
                continue

            selected_answer = selected_answer.upper()

            is_correct = (
                selected_answer == question.correct_answer.upper()
            )

            if is_correct:
                correct_count += 1

            Answer.objects.create(
                attempt=attempt,
                question=question,
                selected_answer=selected_answer,
                is_correct=is_correct,
            )

        attempt.score = correct_count
        attempt.save()

        # IMPORTANT:
        # Do not return score, correct answers, or explanations.
        return Response(
            {
                "message": "Quiz submitted successfully."
            },
            status=status.HTTP_201_CREATED,
        )

class QuizAttemptResultsView(APIView):
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        attempts = QuizAttempt.objects.select_related(
            "student__user",
            "quiz"
        ).prefetch_related(
            "answers__question"
        )

        results = []

        for attempt in attempts:
            answers = []

            for answer in attempt.answers.all():
                answers.append({
                    "question": answer.question.id,
                    "question_text": answer.question.question_text,
                    "student_answer": answer.selected_answer,
                    "correct_answer": answer.question.correct_answer,
                    "correct": answer.is_correct,
                })

            results.append({
                "id": attempt.id,
                "student": attempt.student.user.username,
                "quiz": attempt.quiz.title,
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "attempted_at": attempt.attempted_at,
                "answers": answers,
            })

        return Response(results)

class TopicPerformanceView(APIView):
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        attempts = QuizAttempt.objects.select_related(
            "student__user",
            "quiz__topic"
        ).prefetch_related(
            "answers"
        )

        performance = {}

        for attempt in attempts:
            topic = attempt.quiz.topic
            topic_id = topic.id

            if topic_id not in performance:
                performance[topic_id] = {
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "students": {},
                }

            student_id = attempt.student.id

            if student_id not in performance[topic_id]["students"]:
                performance[topic_id]["students"][student_id] = {
                    "student_id": student_id,
                    "student_username": attempt.student.user.username,
                    "correct": 0,
                    "total": 0,
                }

            student_data = performance[topic_id]["students"][student_id]

            for answer in attempt.answers.all():
                student_data["total"] += 1

                if answer.is_correct:
                    student_data["correct"] += 1

        results = []

        for topic_data in performance.values():
            students = []

            for student_data in topic_data["students"].values():
                total = student_data["total"]
                correct = student_data["correct"]

                percentage = (
                    (correct / total) * 100
                    if total > 0
                    else 0
                )

                students.append({
                    "student_id": student_data["student_id"],
                    "student_username": student_data["student_username"],
                    "correct": correct,
                    "total": total,
                    "percentage": round(percentage, 2),
                })

            results.append({
                "topic_id": topic_data["topic_id"],
                "topic_name": topic_data["topic_name"],
                "students": students,
            })

        return Response(results)

class MyTopicPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.student
        except Exception:
            return Response(
                {"error": "Only students can access their performance."},
                status=status.HTTP_403_FORBIDDEN,
            )

        attempts = QuizAttempt.objects.filter(
            student=student
        ).select_related(
            "quiz__topic"
        ).prefetch_related(
            "answers"
        )

        performance = {}

        for attempt in attempts:
            topic = attempt.quiz.topic
            topic_id = topic.id

            if topic_id not in performance:
                performance[topic_id] = {
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "correct": 0,
                    "total": 0,
                }

            for answer in attempt.answers.all():
                performance[topic_id]["total"] += 1

                if answer.is_correct:
                    performance[topic_id]["correct"] += 1

        results = []

        for topic_data in performance.values():
            total = topic_data["total"]
            correct = topic_data["correct"]

            percentage = (
                (correct / total) * 100
                if total > 0
                else 0
            )

            if percentage < 50:
                level = "weak"
            elif percentage < 70:
                level = "developing"
            elif percentage < 85:
                level = "good"
            else:
                level = "strong"

            results.append({
                "topic_id": topic_data["topic_id"],
                "topic_name": topic_data["topic_name"],
                "correct": correct,
                "total": total,
                "percentage": round(percentage, 2),
                "level": level,
            })

        return Response(results)