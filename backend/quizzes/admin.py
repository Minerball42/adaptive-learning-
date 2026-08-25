from django.contrib import admin

from .models import (
    Quiz,
    Question,
    AdaptiveQuizSession,
)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "topic",
    )

    search_fields = (
        "title",
        "topic__name",
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quiz",
        "difficulty",
        "question_text",
    )

    list_filter = (
        "difficulty",
        "quiz",
    )

    search_fields = (
        "question_text",
    )


@admin.register(AdaptiveQuizSession)
class AdaptiveQuizSessionAdmin(
    admin.ModelAdmin
):
    list_display = (
        "id",
        "student",
        "quiz",
        "target_difficulty",
        "status",
        "created_at",
        "expires_at",
        "submitted_at",
    )

    list_filter = (
        "status",
        "target_difficulty",
        "created_at",
    )

    search_fields = (
        "student__user__username",
        "quiz__title",
    )

    readonly_fields = (
        "id",
        "created_at",
        "submitted_at",
    )

    filter_horizontal = (
        "questions",
    )