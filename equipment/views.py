from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import DetailView, ListView

from .models import Equipment


class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"
    context_object_name = "equipments"
    paginate_by = 20


class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = "equipment/equipment_detail.html"
    context_object_name = "equipment"


def equipment_create(request):
    return HttpResponse("Crear equipo")


def equipment_update(request, pk):
    return HttpResponse(f"Editar equipo {pk}")


def equipment_retire(request, pk):
    return HttpResponse(f"Retirar equipo {pk}")
