from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from equipment.models import Equipment

from .forms import MaintenanceForm
from .models import MaintenanceRecord


class MaintenanceListView(LoginRequiredMixin, ListView):
    model = MaintenanceRecord
    template_name = "maintenance/maintenance_list.html"
    context_object_name = "maintenance_records"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("equipment", "performed_by")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(description__icontains=query)
                | Q(equipment__name__icontains=query)
                | Q(equipment__code__icontains=query)
            )

        maintenance_type = self.request.GET.get("type")
        valid_types = {value for value, _ in MaintenanceRecord.MaintenanceType.choices}
        if maintenance_type in valid_types:
            queryset = queryset.filter(maintenance_type=maintenance_type)

        status = self.request.GET.get("status")
        valid_statuses = {value for value, _ in MaintenanceRecord.Status.choices}
        if status in valid_statuses:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["query_params"] = query_params.urlencode()
        context["maintenance_type_choices"] = MaintenanceRecord.MaintenanceType.choices
        context["status_choices"] = MaintenanceRecord.Status.choices
        return context


class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceRecord
    template_name = "maintenance/maintenance_detail.html"
    context_object_name = "maintenance_record"


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceForm
    template_name = "maintenance/maintenance_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.performed_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("maintenance:list")


class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceRecord
    form_class = MaintenanceForm
    template_name = "maintenance/maintenance_form.html"

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("maintenance:detail", args=[self.object.pk])


class MaintenanceHistoryView(LoginRequiredMixin, ListView):
    template_name = "maintenance/maintenance_history.html"
    context_object_name = "maintenance_records"
    paginate_by = 20

    def get_queryset(self):
        self.equipment = get_object_or_404(Equipment, pk=self.kwargs["equipment_id"])
        return MaintenanceRecord.objects.filter(
            equipment=self.equipment
        ).select_related("performed_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["equipment"] = self.equipment
        return context
