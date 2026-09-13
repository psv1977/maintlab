from django.contrib import admin
from django.contrib.auth.models import User

from .models import Customer, Organization
from .tenant import get_user_organization


class OrganizationScopedAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(organization=get_user_organization(request.user))

    def save_model(self, request, obj, form, change):
        if not change:
            obj.organization = get_user_organization(request.user)
        super().save_model(request, obj, form, change)


@admin.register(Customer)
class CustomerAdmin(OrganizationScopedAdmin):
    list_display = ("name", "rut", "customer_type")
    list_filter = ("customer_type",)
    search_fields = ("name", "rut")

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(User)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "rut", "account_status", "demo_ends_at", "subscription_ends_at")
    list_filter = ("account_status",)
    search_fields = ("name", "rut")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
