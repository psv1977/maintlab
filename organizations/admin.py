from django.contrib import admin
from django.contrib.auth.models import User

from .tenant import get_user_organization


class OrganizationScopedAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(organization=get_user_organization(request.user))

    def save_model(self, request, obj, form, change):
        if not change:
            obj.organization = get_user_organization(request.user)
        super().save_model(request, obj, form, change)


admin.site.unregister(User)
