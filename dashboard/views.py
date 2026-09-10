from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from equipment.models import Equipment
from maintenance.models import MaintenanceRecord, WorkOrder


class DashboardView(LoginRequiredMixin, TemplateView):
    """Vista de inicio que muestra un resumen del sistema."""

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Equipos por estado
        equipment_counts = {}
        for value, label in Equipment.Status.choices:
            equipment_counts[value] = {
                "label": label,
                "count": Equipment.objects.filter(status=value).count(),
            }
        context["equipment_by_status"] = equipment_counts

        # Mantenimientos por estado
        maintenance_counts = {}
        for value, label in MaintenanceRecord.Status.choices:
            maintenance_counts[value] = {
                "label": label,
                "count": MaintenanceRecord.objects.filter(status=value).count(),
            }
        context["maintenance_by_status"] = maintenance_counts

        # Órdenes de trabajo
        context["total_work_orders"] = WorkOrder.objects.count()

        # Últimos 5 equipos
        context["recent_equipments"] = (
            Equipment.objects.select_related("location")
            .order_by("-created_at")[:5]
        )

        # Últimos 5 mantenimientos
        context["recent_maintenances"] = (
            MaintenanceRecord.objects.select_related("equipment", "performed_by")
            .order_by("-performed_at")[:5]
        )

        # Próximos mantenimientos (próximos 30 días)
        context["upcoming_maintenances"] = (
            MaintenanceRecord.objects.filter(
                next_maintenance__gte=now,
                next_maintenance__lte=now + timezone.timedelta(days=30),
            )
            .select_related("equipment")
            .order_by("next_maintenance")[:10]
        )

        return context
