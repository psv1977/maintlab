from django.contrib import admin

from .models import Equipment, EquipmentIdentifier, Location, MeterReading
from organizations.admin import OrganizationScopedAdmin


@admin.register(Location)
class LocationAdmin(OrganizationScopedAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Equipment)
class EquipmentAdmin(OrganizationScopedAdmin):
    list_display = [
        "name",
        "customer",
        "code",
        "brand",
        "model",
        "location",
        "equipment_type",
        "status",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    ]
    list_filter = ["status", "equipment_type"]
    search_fields = ["name", "code", "serial_number", "brand", "model", "application", "customer__rut", "customer__name"]
    readonly_fields = [
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    ]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MeterReading)
class MeterReadingAdmin(OrganizationScopedAdmin):
    list_display = ["equipment", "value", "recorded_at", "recorded_by"]
    list_filter = ["equipment__equipment_type"]
    search_fields = ["equipment__name", "equipment__code"]
    readonly_fields = ["organization", "recorded_by"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.organization = obj.equipment.organization
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EquipmentIdentifier)
class EquipmentIdentifierAdmin(OrganizationScopedAdmin):
    list_display = ["identifier_type", "value", "equipment"]
    list_filter = ["identifier_type"]
    search_fields = ["value", "equipment__name", "equipment__code"]

    def has_delete_permission(self, request, obj=None):
        return False
