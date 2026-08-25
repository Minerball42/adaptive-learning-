from django.contrib import admin

from .models import (
    Board,
    AcademicYear,
    Grade,
    Subject,
    Chapter,
    Topic,
    LearningContent,
    Note,
)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "state",
        "country",
        "is_active",
    )

    list_filter = (
        "is_active",
        "state",
        "country",
    )

    search_fields = (
        "code",
        "name",
    )


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "board",
        "is_active",
    )

    list_filter = (
        "board",
        "is_active",
    )

    search_fields = (
        "name",
        "board__name",
        "board__code",
    )


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "level",
        "academic_year",
    )

    list_filter = (
        "level",
        "academic_year__board",
        "academic_year",
    )

    search_fields = (
        "name",
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "grade",
        "language",
    )

    list_filter = (
        "language",
        "grade",
    )

    search_fields = (
        "name",
    )


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):

    list_display = (
        "chapter_number",
        "name",
        "subject",
    )

    list_filter = (
        "subject",
    )

    search_fields = (
        "name",
        "subject__name",
    )

    ordering = (
        "subject",
        "chapter_number",
    )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "chapter",
        "difficulty",
    )

    list_filter = (
        "difficulty",
        "chapter__subject",
    )

    search_fields = (
        "name",
        "chapter__name",
    )


@admin.register(LearningContent)
class LearningContentAdmin(admin.ModelAdmin):

    list_display = (
        "topic",
        "updated_at",
    )

    search_fields = (
        "topic__name",
    )


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "chapter",
        "uploaded_at",
    )

    search_fields = (
        "title",
        "chapter__name",
    )