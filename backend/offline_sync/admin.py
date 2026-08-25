from django.contrib import admin

from .models import OfflineSyncRecord


@admin.register(OfflineSyncRecord)
class OfflineSyncRecordAdmin(
    admin.ModelAdmin
):
    list_display = (
        "id",
        "student",
        "client_attempt_id",
        "status",
        "device_id",
        "received_at",
        "synced_at",
    )

    list_filter = (
        "status",
        "received_at",
    )

    search_fields = (
        "student__user__username",
        "client_attempt_id",
        "device_id",
    )

    readonly_fields = (
        "id",
        "received_at",
    )