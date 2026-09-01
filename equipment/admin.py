from django.contrib import admin

from .models import Equipment, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "brand",
        "model",
        "location",
        "status",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    ]
    list_filter = ["status"]
    search_fields = ["name", "code", "serial_number", "brand", "model", "application"]
    readonly_fields = [
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    ]

    def has_delete_permission(self, request, obj=None):
        return False
