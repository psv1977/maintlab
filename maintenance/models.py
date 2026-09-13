from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from equipment.models import Equipment
from organizations.models import Organization, default_organization


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
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="work_orders", default=default_organization)
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


class MaintenancePlan(models.Model):
    class Strategy(models.TextChoices):
        TIME = "time", "Tiempo"
        METER = "meter", "Horómetro / kilometraje"

    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="maintenance_plans", default=default_organization)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name="maintenance_plans")
    name = models.CharField(max_length=200)
    strategy = models.CharField(max_length=20, choices=Strategy.choices)
    interval_days = models.PositiveIntegerField(null=True, blank=True)
    interval_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)
    last_service_at = models.DateTimeField(default=timezone.now)
    last_service_meter = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="maintenance_plans_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["equipment", "name"]
        verbose_name = "plan de mantenimiento"
        verbose_name_plural = "planes de mantenimiento"

    def clean(self):
        errors = {}
        if self.equipment_id and self.organization_id and self.equipment.organization_id != self.organization_id:
            errors["equipment"] = "El equipo debe pertenecer a la misma empresa del plan."
        if self.strategy == self.Strategy.TIME:
            if not self.interval_days:
                errors["interval_days"] = "Indique el intervalo en días."
            if self.interval_value is not None:
                errors["interval_value"] = "Un plan por tiempo no usa una lectura de medidor."
        elif self.strategy == self.Strategy.METER:
            if self.interval_value is None or self.interval_value <= 0:
                errors["interval_value"] = "Indique un intervalo de uso mayor que cero."
            if self.interval_days is not None:
                errors["interval_days"] = "Un plan por uso no usa días."
        if errors:
            raise ValidationError(errors)

    @property
    def next_service_at(self):
        if self.strategy != self.Strategy.TIME or not self.last_service_at:
            return None
        from datetime import timedelta
        return self.last_service_at + timedelta(days=self.interval_days)

    @property
    def next_service_meter(self):
        if self.strategy != self.Strategy.METER or self.last_service_meter is None:
            return None
        return Decimal(str(self.last_service_meter)) + Decimal(str(self.interval_value))

    def is_due(self, *, at=None, meter_value=None):
        if not self.active:
            return False
        at = at or timezone.now()
        if self.strategy == self.Strategy.TIME:
            return bool(self.next_service_at and at >= self.next_service_at)
        return bool(
            meter_value is not None
            and self.next_service_meter is not None
            and Decimal(str(meter_value)) >= self.next_service_meter
        )

    def __str__(self):
        return f"{self.equipment} - {self.name}"


class MaintenanceRecord(models.Model):

    class MaintenanceType(models.TextChoices):
        SCHEDULED = "scheduled", "Programado"
        UNSCHEDULED = "unscheduled", "No programado"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        IN_PROGRESS = "in_progress", "En curso"
        COMPLETED = "completed", "Completado"

    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="maintenance_records", default=default_organization)
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
    reset_plans = models.ManyToManyField(
        MaintenancePlan,
        blank=True,
        related_name="reset_by_maintenances",
    )
    maintenance_type = models.CharField(
        max_length=20,
        choices=MaintenanceType.choices,
    )
    description = models.TextField()
    meter_reading = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
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
