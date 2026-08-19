from django.contrib.auth import authenticate
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Grade
from .models import Student, Teacher
from .serializers import StudentProfileSerializer, StudentRegisterSerializer


class StudentRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)

        if serializer.is_valid():
            student = serializer.save()

            token, created = Token.objects.get_or_create(
                user=student.user
            )

            return Response(
                {
                    "message": "Student registered successfully.",
                    "token": token.key,
                    "student": StudentProfileSerializer(student).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class StudentLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not hasattr(user, "student"):
            return Response(
                {"error": "This account is not registered as a student."},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "Login successful.",
                "token": token.key,
                "student": StudentProfileSerializer(
                    user.student
                ).data,
            }
        )


class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            return Response(
                {"error": "Student profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            StudentProfileSerializer(student).data
        )

class IsTeacherOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Django admin/superuser
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Registered teacher
        return Teacher.objects.filter(user=request.user).exists()

class AssignStudentGradeView(APIView):
    permission_classes = [IsTeacherOrAdmin]

    def post(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {"error": "Student not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        grade_id = request.data.get("grade")

        if not grade_id:
            return Response(
                {"error": "Grade ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return Response(
                {"error": "Grade not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        student.grade = grade
        student.save(update_fields=["grade"])

        return Response(
            {
                "message": "Student grade assigned successfully.",
                "student": StudentProfileSerializer(student).data,
            },
            status=status.HTTP_200_OK,
        )

class TeacherLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not hasattr(user, "teacher"):
            return Response(
                {"error": "This account is not registered as a teacher."},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, created = Token.objects.get_or_create(user=user)

        teacher = user.teacher

        return Response(
            {
                "message": "Teacher login successful.",
                "token": token.key,
                "teacher": {
                    "username": user.username,
                    "email": user.email,
                    "school": teacher.school,
                },
            }
        )

