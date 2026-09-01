from django.conf import settings
from django.db import models

from equipment.models import Equipment


class DocumentSequence(models.Model):
    document_type = models.CharField(max_length=50, unique=True)
    next_number = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "secuencia documental"
        verbose_name_plural = "secuencias documentales"

    def __str__(self):
        return self.document_type


class WorkOrder(models.Model):
    number = models.CharField(max_length=20, unique=True, editable=False)
    client_rut = models.CharField(max_length=20, blank=True, db_index=True)
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="work_orders",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="work_orders_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "orden de trabajo"
        verbose_name_plural = "órdenes de trabajo"

    def __str__(self):
        return self.number


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
    work_order = models.OneToOneField(
        WorkOrder,
        on_delete=models.PROTECT,
        related_name="maintenance_record",
        null=True,
        blank=True,
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
    completed_at = models.DateTimeField(null=True, blank=True)
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
