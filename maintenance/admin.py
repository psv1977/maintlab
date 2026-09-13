from django.contrib import admin

from .models import MaintenancePlan, MaintenanceRecord, WorkOrder
from organizations.admin import OrganizationScopedAdmin


@admin.register(WorkOrder)
class WorkOrderAdmin(OrganizationScopedAdmin):
    list_display = ["number", "client_rut", "equipment", "created_by", "created_at"]
    search_fields = ["number", "client_rut", "equipment__name", "equipment__code"]
    readonly_fields = ["number", "created_by", "created_at"]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(OrganizationScopedAdmin):
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


@admin.register(MaintenancePlan)
class MaintenancePlanAdmin(OrganizationScopedAdmin):
    list_display = ["name", "equipment", "strategy", "interval_days", "interval_value", "active"]
    list_filter = ["strategy", "active"]
    search_fields = ["name", "equipment__name", "equipment__code"]
    readonly_fields = ["created_by", "created_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.organization = obj.equipment.organization
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False
