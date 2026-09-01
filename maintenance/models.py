from django.conf import settings
from django.db import models

from equipment.models import Equipment


class MaintenanceRecord(models.Model):

    class MaintenanceType(models.TextChoices):
        SCHEDULED = "scheduled", "Programado"
        UNSCHEDULED = "unscheduled", "No programado"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        IN_PROGRESS = "in_progress", "En curso"
        COMPLETED = "completed", "Completado"

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="maintenance_records",
    )
    maintenance_type = models.CharField(
        max_length=20,
        choices=MaintenanceType.choices,
    )
    description = models.TextField()
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(class)s_performed",
    )
    performed_at = models.DateTimeField()
    next_maintenance = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    notes = models.TextField(blank=True)

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
        ordering = ["-performed_at"]
        verbose_name = "registro de mantenimiento"
        verbose_name_plural = "registros de mantenimiento"

    def __str__(self):
        return f"{self.equipment.name} - {self.get_maintenance_type_display()}"
