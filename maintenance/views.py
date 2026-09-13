from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from equipment.models import Equipment

from .forms import MaintenanceForm, MaintenancePlanForm
from .models import DocumentSequence, MaintenancePlan, MaintenanceRecord, WorkOrder
from .queries import due_maintenance_plans, open_maintenance_records
from organizations.tenant import get_user_organization


def allocate_work_order_number():
    sequence, _ = DocumentSequence.objects.get_or_create(
        document_type="work_order",
        defaults={"next_number": 1},
    )
    sequence = DocumentSequence.objects.select_for_update().get(pk=sequence.pk)
    number = f"OT-{sequence.next_number:04d}"
    sequence.next_number += 1
    sequence.save(update_fields=["next_number", "updated_at"])
    return number


class MaintenanceListView(LoginRequiredMixin, ListView):
    model = MaintenanceRecord
    template_name = "maintenance/maintenance_list.html"
    context_object_name = "maintenance_records"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(organization=get_user_organization(self.request.user)).select_related(
            "equipment", "performed_by", "work_order"
        )
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(description__icontains=query)
                | Q(equipment__name__icontains=query)
                | Q(equipment__code__icontains=query)
                | Q(work_order__number__icontains=query)
                | Q(work_order__client_rut__icontains=query)
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


class MaintenancePendingView(LoginRequiredMixin, ListView):
    """Separa los trabajos abiertos de los planes que alcanzaron su vencimiento."""

    template_name = "maintenance/maintenance_pending.html"
    context_object_name = "results"
    paginate_by = 20

    def get_queryset(self):
        organization = get_user_organization(self.request.user)
        self.equipment = None
        if "equipment_id" in self.kwargs:
            self.equipment = get_object_or_404(
                Equipment, pk=self.kwargs["equipment_id"], organization=organization,
            )
        self.category = "due" if self.request.GET.get("category") == "due" else "open"
        self.query = self.request.GET.get("q", "").strip()
        records = open_maintenance_records(organization)
        plans = due_maintenance_plans(organization)
        if self.equipment:
            records = records.filter(equipment=self.equipment)
            plans = plans.filter(equipment=self.equipment)
        if self.query:
            equipment_match = (
                Q(equipment__name__icontains=self.query)
                | Q(equipment__code__icontains=self.query)
                | Q(equipment__serial_number__icontains=self.query)
                | Q(equipment__location__name__icontains=self.query)
            )
            records = records.filter(
                equipment_match | Q(description__icontains=self.query)
                | Q(work_order__number__icontains=self.query)
                | Q(work_order__client_rut__icontains=self.query)
            )
            plans = plans.filter(equipment_match | Q(name__icontains=self.query))
        self.open_count = records.count()
        self.due_count = plans.count()
        return plans if self.category == "due" else records.order_by("performed_at", "pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context.update(
            equipment=self.equipment, category=self.category, query=self.query,
            open_count=self.open_count, due_count=self.due_count,
            query_params=params.urlencode(),
        )
        return context


class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceRecord
    template_name = "maintenance/maintenance_detail.html"
    context_object_name = "maintenance_record"

    def get_queryset(self):
        return super().get_queryset().filter(organization=get_user_organization(self.request.user))


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceForm
    template_name = "maintenance/maintenance_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = get_user_organization(self.request.user)
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.created_by = self.request.user
            form.instance.organization = get_user_organization(self.request.user)
            form.instance.performed_by = self.request.user
            work_order = WorkOrder.objects.create(
                number=allocate_work_order_number(),
                organization=form.instance.organization,
                client_rut=form.cleaned_data["client_rut"],
                equipment=form.cleaned_data["equipment"],
                created_by=self.request.user,
            )
            form.instance.work_order = work_order
            response = super().form_valid(form)
            self._reset_plans(form)
        return response

    def _reset_plans(self, form):
        plans = form.cleaned_data.get("reset_plans", [])
        form.instance.reset_plans.set(plans)
        for plan in plans:
            plan.last_service_at = form.instance.performed_at
            if plan.strategy == plan.Strategy.METER:
                plan.last_service_meter = form.cleaned_data.get("meter_reading")
            plan.save(update_fields=["last_service_at", "last_service_meter"])

    def get_success_url(self):
        return reverse("maintenance:list")


class MaintenancePlanCreateView(LoginRequiredMixin, CreateView):
    model = MaintenancePlan
    form_class = MaintenancePlanForm
    template_name = "maintenance/maintenance_plan_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = get_user_organization(self.request.user)
        return kwargs

    def form_valid(self, form):
        form.instance.organization = get_user_organization(self.request.user)
        form.instance.created_by = self.request.user
        if form.instance.strategy == MaintenancePlan.Strategy.METER:
            latest_reading = form.instance.equipment.meter_readings.order_by(
                "-recorded_at", "-pk"
            ).first()
            if latest_reading:
                form.instance.last_service_meter = latest_reading.value
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("equipment:detail", args=[self.object.equipment_id])


class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceRecord
    form_class = MaintenanceForm
    template_name = "maintenance/maintenance_form.html"

    def get_queryset(self):
        return super().get_queryset().filter(organization=get_user_organization(self.request.user))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = get_user_organization(self.request.user)
        return kwargs

    def form_valid(self, form):
        if form.instance.work_order_id:
            form.instance.work_order.client_rut = form.cleaned_data["client_rut"]
            form.instance.work_order.save(update_fields=["client_rut"])
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
        self.equipment = get_object_or_404(Equipment, pk=self.kwargs["equipment_id"], organization=get_user_organization(self.request.user))
        return MaintenanceRecord.objects.filter(
            equipment=self.equipment, organization=get_user_organization(self.request.user)
        ).select_related("performed_by", "work_order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["equipment"] = self.equipment
        return context
