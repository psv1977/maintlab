from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import EquipmentForm, EquipmentImportForm, LocationForm
from .models import Equipment, Location
from organizations.tenant import get_user_organization


class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"
    context_object_name = "equipments"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(organization=get_user_organization(self.request.user))
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(code__icontains=query)
                | Q(name__icontains=query)
                | Q(serial_number__icontains=query)
            )

        status = self.request.GET.get("status")
        valid_statuses = {value for value, _ in Equipment.Status.choices}
        if status in valid_statuses:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["query_params"] = query_params.urlencode()
        context["status_choices"] = Equipment.Status.choices
        return context


class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = "equipment/equipment_detail.html"
    context_object_name = "equipment"

    def get_queryset(self):
        return super().get_queryset().filter(organization=get_user_organization(self.request.user))


class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/equipment_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = get_user_organization(self.request.user)
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.organization = get_user_organization(self.request.user)
        form.instance.status = Equipment.Status.OPERATIONAL
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("equipment:list")


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "equipment/location_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = get_user_organization(self.request.user)
        return kwargs

    def form_valid(self, form):
        form.instance.organization = get_user_organization(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("equipment:create")


class EquipmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/equipment_form.html"

    def get_queryset(self):
        return super().get_queryset().filter(organization=get_user_organization(self.request.user))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = get_user_organization(self.request.user)
        return kwargs

    def form_valid(self, form):
        if form.instance.status == Equipment.Status.RETIRED:
            form.add_error("status", "No puede asignar el estado Retirado.")
            return self.form_invalid(form)
        form.instance.updated_by = self.request.user
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("equipment:detail", args=[self.object.pk])


class EquipmentRetireView(PermissionRequiredMixin, View):
    permission_required = "equipment.retire_equipment"
    template_name = "equipment/equipment_confirm_retire.html"

    def get(self, request, pk):
        equipment = get_object_or_404(Equipment, pk=pk, organization=get_user_organization(request.user))
        return render(request, self.template_name, {"equipment": equipment})

    def post(self, request, pk):
        equipment = get_object_or_404(Equipment, pk=pk, organization=get_user_organization(request.user))
        equipment.status = Equipment.Status.RETIRED
        equipment.save(update_fields=["status"])
        return redirect(reverse("equipment:detail", args=[equipment.pk]))


class EquipmentImportView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "equipment/equipment_import.html"

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        return render(request, self.template_name, {"form": EquipmentImportForm()})

    def post(self, request):
        form = EquipmentImportForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        from openpyxl import load_workbook

        workbook = load_workbook(form.cleaned_data["file"], read_only=True, data_only=True)
        worksheet = workbook.active
        headers = [str(value).strip().lower() if value is not None else "" for value in next(worksheet.iter_rows(values_only=True), ())]
        required_headers = ["name", "code"]
        if any(header not in headers for header in required_headers):
            form.add_error("file", "La planilla debe incluir las columnas name y code.")
            return render(request, self.template_name, {"form": form})

        organization = get_user_organization(request.user)
        rows = []
        errors = []
        seen_codes = set()
        for row_number, values in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
            if not any(value is not None for value in values):
                continue
            data = dict(zip(headers, values))
            name = str(data.get("name") or "").strip()
            code = str(data.get("code") or "").strip()
            if not name or not code:
                errors.append(f"Fila {row_number}: name y code son obligatorios.")
            elif code in seen_codes or Equipment.objects.filter(organization=organization, code=code).exists():
                errors.append(f"Fila {row_number}: el código {code} ya existe.")
            else:
                seen_codes.add(code)
                rows.append(data)

        if errors:
            return render(request, self.template_name, {"form": form, "errors": errors})

        with transaction.atomic():
            for data in rows:
                location_name = str(data.get("location") or "").strip()
                location = None
                if location_name:
                    location, _ = Location.objects.get_or_create(organization=organization, name=location_name)
                Equipment.objects.create(
                    organization=organization,
                    name=str(data["name"]).strip(),
                    code=str(data["code"]).strip(),
                    description=str(data.get("description") or "").strip(),
                    serial_number=str(data.get("serial_number") or "").strip(),
                    brand=str(data.get("brand") or "").strip(),
                    model=str(data.get("model") or "").strip(),
                    location=location,
                    application=str(data.get("application") or "").strip(),
                    created_by=request.user,
                )
        return render(request, self.template_name, {"form": EquipmentImportForm(), "imported_count": len(rows)})
