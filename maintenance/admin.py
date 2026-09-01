from django.contrib import admin

from .models import DocumentSequence, MaintenanceRecord, WorkOrder


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ["number", "client_rut", "equipment", "created_by", "created_at"]
    search_fields = ["number", "client_rut", "equipment__name", "equipment__code"]
    readonly_fields = ["number", "created_by", "created_at"]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DocumentSequence)
class DocumentSequenceAdmin(admin.ModelAdmin):
    list_display = ["document_type", "next_number", "updated_at"]


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        "work_order",
        "equipment",
        "maintenance_type",
        "status",
        "performed_by",
        "performed_at",
        "completed_at",
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
