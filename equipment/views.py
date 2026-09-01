from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import EquipmentForm
from .models import Equipment


class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"
    context_object_name = "equipments"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
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


class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/equipment_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = Equipment.Status.OPERATIONAL
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("equipment:list")


class EquipmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/equipment_form.html"

    def form_valid(self, form):
        if form.instance.status == Equipment.Status.RETIRED:
            form.add_error("status", "No puede asignar el estado Retirado.")
            return self.form_invalid(form)
        form.instance.updated_by = self.request.user
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("equipment:detail", args=[self.object.pk])


def equipment_retire(request, pk):
    return HttpResponse(f"Retirar equipo {pk}")
