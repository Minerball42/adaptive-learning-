from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Student


class StudentRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = Student
        fields = [
            "username",
            "password",
            "email",
            "school",
            "preferred_language",
        ]

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        email = validated_data.pop("email", "")

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        student = Student.objects.create(
            user=user,
            **validated_data,
        )

        return student


class StudentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "username",
            "email",
            "grade",
            "school",
            "preferred_language",
        ]