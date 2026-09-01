from django.db import models
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class PasswordHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_history",
    )
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "historial de contraseña"
        verbose_name_plural = "historial de contraseñas"

    def matches(self, raw_password):
        return check_password(raw_password, self.password)
