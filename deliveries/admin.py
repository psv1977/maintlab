from django.contrib import admin

from .models import Delivery
from organizations.admin import OrganizationScopedAdmin


@admin.register(Delivery)
class DeliveryAdmin(OrganizationScopedAdmin):
    list_display = ["equipment", "client_name", "client_rut", "status", "delivered_at"]
    list_filter = ["status"]
    search_fields = ["equipment__name", "equipment__code", "client_name", "client_rut"]
