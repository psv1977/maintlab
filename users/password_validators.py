from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import PasswordHistory


class PasswordReuseValidator:
    def validate(self, password, user=None):
        if user and user.pk and any(
            history.matches(password) for history in user.password_history.all()
        ):
            raise ValidationError(
                _("La nueva contraseña no puede coincidir con una contraseña anterior."),
                code="password_reused",
            )

    def get_help_text(self):
        return _("La nueva contraseña no puede reutilizar una contraseña anterior.")

    def password_changed(self, password, user=None):
        if user:
            PasswordHistory.objects.create(user=user, password=user.password)
