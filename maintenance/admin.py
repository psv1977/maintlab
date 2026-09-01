from django.contrib import admin

from .models import MaintenanceRecord


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        "equipment",
        "maintenance_type",
        "status",
        "performed_by",
        "performed_at",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    ]
    list_filter = ["status", "maintenance_type"]
    search_fields = ["description", "equipment__name", "equipment__code"]
    readonly_fields = [
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    ]

    def has_delete_permission(self, request, obj=None):
        return False
