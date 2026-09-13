from datetime import timedelta

from django.db.models import DateTimeField, DurationField, ExpressionWrapper, F, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Cast
from django.utils import timezone

from equipment.models import MeterReading

from .models import MaintenancePlan, MaintenanceRecord


def open_maintenance_records(organization):
    """Devuelve trabajos pendientes o en curso de la empresa."""
    return MaintenanceRecord.objects.filter(
        organization=organization,
        equipment__organization=organization,
        status__in=[MaintenanceRecord.Status.PENDING, MaintenanceRecord.Status.IN_PROGRESS],
    ).select_related("equipment", "equipment__location", "work_order")


def due_maintenance_plans(organization, *, at=None):
    """Consulta vencimientos por fecha o última lectura disponible, sin crear trabajos."""
    at = at or timezone.now()
    latest_reading = MeterReading.objects.filter(
        organization=organization,
        equipment_id=OuterRef("equipment_id"),
        recorded_at__lte=at,
    ).order_by("-recorded_at", "-pk")
    return (
        MaintenancePlan.objects.filter(
            organization=organization, equipment__organization=organization, active=True,
        )
        .annotate(
            latest_meter_value=Subquery(latest_reading.values("value")[:1]),
            due_at=ExpressionWrapper(
                F("last_service_at") + ExpressionWrapper(
                    Cast("interval_days", IntegerField()) * timedelta(days=1),
                    output_field=DurationField(),
                ),
                output_field=DateTimeField(),
            ),
            due_meter=F("last_service_meter") + F("interval_value"),
        )
        .filter(
            Q(strategy=MaintenancePlan.Strategy.TIME, interval_days__gt=0, due_at__lte=at)
            | Q(
                strategy=MaintenancePlan.Strategy.METER,
                interval_value__gt=0,
                latest_meter_value__gte=F("due_meter"),
            )
        )
        .select_related("equipment", "equipment__location")
        .order_by("equipment__name", "name", "pk")
    )
