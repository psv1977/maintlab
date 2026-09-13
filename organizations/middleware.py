from django.shortcuts import render

from .tenant import get_user_organization


class OrganizationReadOnlyMiddleware:
    """Bloquea escrituras cuando la cuenta demo o suscripción ha vencido."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not request.user.is_superuser
            and request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and not request.path.startswith("/accounts/logout/")
        ):
            organization = get_user_organization(request.user)
            if organization.is_read_only:
                return render(
                    request,
                    "organizations/read_only.html",
                    {"organization": organization},
                    status=403,
                )
        return self.get_response(request)
