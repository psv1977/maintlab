from django import forms
from django.contrib.auth.models import User

from equipment.models import Equipment
from maintenance.models import WorkOrder
from maintenance.rut import normalize_rut

from .models import Delivery


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = [
            "equipment",
            "work_order",
            "client_name",
            "client_rut",
            "delivered_by",
            "received_by",
            "delivered_at",
            "returned_at",
            "status",
            "notes",
        ]
        labels = {
            "equipment": "Equipo",
            "work_order": "Orden de trabajo",
            "client_name": "Cliente",
            "client_rut": "RUT del cliente",
            "delivered_by": "Responsable de entrega",
            "received_by": "Persona que recibe",
            "delivered_at": "Fecha de entrega",
            "returned_at": "Fecha de recepción",
            "status": "Estado",
            "notes": "Observaciones",
        }
        widgets = {
            "client_rut": forms.TextInput(attrs={"data-rut": "true", "autocomplete": "off"}),
            "delivered_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "returned_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment"].queryset = Equipment.objects.exclude(
            status=Equipment.Status.RETIRED
        )
        self.fields["work_order"].queryset = WorkOrder.objects.select_related("equipment")
        if organization:
            self.fields["equipment"].queryset = self.fields["equipment"].queryset.filter(organization=organization)
            self.fields["work_order"].queryset = self.fields["work_order"].queryset.filter(organization=organization)
        self.fields["delivered_by"].queryset = User.objects.filter(is_active=True)

    def clean_client_rut(self):
        return normalize_rut(self.cleaned_data["client_rut"])

    def clean(self):
        cleaned_data = super().clean()
        work_order = cleaned_data.get("work_order")
        equipment = cleaned_data.get("equipment")
        returned_at = cleaned_data.get("returned_at")
        delivered_at = cleaned_data.get("delivered_at")
        status = cleaned_data.get("status")

        if work_order and equipment and work_order.equipment_id != equipment.id:
            self.add_error("work_order", "La orden de trabajo debe pertenecer al equipo seleccionado.")
        if returned_at and delivered_at and returned_at < delivered_at:
            self.add_error("returned_at", "La recepción no puede ser anterior a la entrega.")
        if status == Delivery.Status.RETURNED and not returned_at:
            self.add_error("returned_at", "Indique la fecha de recepción del equipo.")
        return cleaned_data
