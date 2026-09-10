from django.contrib import admin

from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ["equipment", "client_name", "client_rut", "status", "delivered_at"]
    list_filter = ["status"]
    search_fields = ["equipment__name", "equipment__code", "client_name", "client_rut"]
