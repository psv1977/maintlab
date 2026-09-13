from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, Value
from django.db.models.functions import Replace, Upper
from django.utils import timezone
from django.views.generic import TemplateView

from equipment.models import Equipment
from maintenance.models import MaintenanceRecord, WorkOrder
from organizations.models import Customer
from maintenance.queries import due_maintenance_plans, open_maintenance_records
from organizations.tenant import get_user_organization


class DashboardView(LoginRequiredMixin, TemplateView):
    """Vista de inicio que muestra un resumen del sistema."""

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        organization = get_user_organization(self.request.user)
        context["open_maintenance_count"] = open_maintenance_records(organization).count()
        context["due_maintenance_count"] = due_maintenance_plans(organization, at=now).count()

        # Equipos por estado
        equipment_counts = {}
        for value, label in Equipment.Status.choices:
            equipment_counts[value] = {
                "label": label,
                "count": Equipment.objects.filter(organization=organization, status=value).count(),
            }
        context["equipment_by_status"] = equipment_counts

        # Mantenimientos por estado
        maintenance_counts = {}
        for value, label in MaintenanceRecord.Status.choices:
            maintenance_counts[value] = {
                "label": label,
                "count": MaintenanceRecord.objects.filter(organization=organization, status=value).count(),
            }
        context["maintenance_by_status"] = maintenance_counts

        # Órdenes de trabajo
        context["total_work_orders"] = WorkOrder.objects.filter(organization=organization).count()

        # Últimos 5 equipos
        context["recent_equipments"] = (
            Equipment.objects.filter(organization=organization).select_related("location")
            .order_by("-created_at")[:5]
        )

        # Últimos 5 mantenimientos
        context["recent_maintenances"] = (
            MaintenanceRecord.objects.filter(organization=organization).select_related("equipment", "performed_by")
            .order_by("-performed_at")[:5]
        )

        # Próximos mantenimientos (próximos 30 días)
        context["upcoming_maintenances"] = (
            MaintenanceRecord.objects.filter(
                organization=organization,
                next_maintenance__gte=now,
                next_maintenance__lte=now + timezone.timedelta(days=30),
            )
            .select_related("equipment")
            .order_by("next_maintenance")[:10]
        )

        return context


class UniversalSearchView(LoginRequiredMixin, TemplateView):
    """Busca clientes y equipos solo dentro de la empresa del usuario."""

    template_name = "dashboard/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = get_user_organization(self.request.user)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query
        context["customers"] = Customer.objects.none()
        context["equipments"] = Equipment.objects.none()
        if not query:
            return context

        compact_rut = "".join(character for character in query.upper() if character.isalnum())
        customers = Customer.objects.filter(organization=organization).annotate(
            compact_rut=Replace(Replace(Upper(F("rut")), Value("."), Value("")), Value("-"), Value("")),
        )
        context["customers"] = customers.filter(
            Q(name__icontains=query) | Q(compact_rut__icontains=compact_rut)
        )
        context["equipments"] = (
            Equipment.objects.filter(organization=organization)
            .annotate(
                compact_rut=Replace(Replace(Upper(F("customer__rut")), Value("."), Value("")), Value("-"), Value("")),
            )
            .filter(
                Q(name__icontains=query)
                | Q(code__icontains=query)
                | Q(serial_number__icontains=query)
                | Q(brand__icontains=query)
                | Q(model__icontains=query)
                | Q(application__icontains=query)
                | Q(location__name__icontains=query)
                | Q(customer__name__icontains=query)
                | Q(compact_rut__icontains=compact_rut)
                | Q(identifiers__value__icontains=query)
            )
            .select_related("customer", "location")
            .distinct()
            .order_by("name", "pk")
        )
        return context
