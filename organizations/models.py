import secrets
from datetime import timedelta

from django.conf import settings
from django.db import connection, models
from django.utils import timezone


class Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    rut = models.CharField(max_length=20, unique=True, blank=True, null=True)
    business_line = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"

    def __str__(self):
        return self.name


def default_organization():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM organizations_organization WHERE name = %s",
            ["Empresa inicial"],
        )
        row = cursor.fetchone()
    if not row:
        raise RuntimeError("No existe la empresa inicial requerida para asignar datos existentes.")
    return row[0]


class OrganizationMembership(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="memberships"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organization_membership"
    )

    class Meta:
        verbose_name = "asignación de empresa"
        verbose_name_plural = "asignaciones de empresa"

    def __str__(self):
        return f"{self.user} - {self.organization}"


def invitation_expiration():
    return timezone.now() + timedelta(days=7)


class OrganizationInvitation(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="invitations"
    )
    code = models.CharField(max_length=64, unique=True, editable=False)
    expires_at = models.DateTimeField(default=invitation_expiration)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="invitations_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_by = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="invitation_used",
        null=True,
        blank=True,
    )
    used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "invitación"
        verbose_name_plural = "invitaciones"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = secrets.token_urlsafe(18)
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return not self.used_at and not self.revoked_at and self.expires_at > timezone.now()

    def __str__(self):
        return f"Invitación para {self.organization}"
