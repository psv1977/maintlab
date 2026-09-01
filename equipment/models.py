from django.conf import settings
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "ubicación"
        verbose_name_plural = "ubicaciones"

    def __str__(self):
        return self.name


class Equipment(models.Model):

    class Status(models.TextChoices):
        OPERATIONAL = "operational", "Operativo"
        IN_MAINTENANCE = "in_maintenance", "En mantenimiento"
        OUT_OF_SERVICE = "out_of_service", "Fuera de servicio"
        RETIRED = "retired", "Retirado"

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="equipments",
        null=True,
        blank=True,
    )
    commissioned_at = models.DateField(null=True, blank=True)
    application = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPERATIONAL,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(class)s_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(class)s_updated",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        permissions = [
            ("retire_equipment", "Can retire equipment"),
        ]

    def __str__(self):
        return self.name
