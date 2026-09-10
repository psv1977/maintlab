from django import forms
from django.contrib.auth.models import User

from equipment.models import Equipment

from .models import MaintenanceRecord
from .rut import normalize_rut


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            "equipment",
            "client_rut",
            "maintenance_type",
            "description",
            "performed_by",
            "performed_at",
            "completed_at",
            "next_maintenance",
            "status",
            "notes",
        ]
        widgets = {
            "performed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "completed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "next_maintenance": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        labels = {
            "equipment": "Equipo",
            "maintenance_type": "Tipo de mantenimiento",
            "description": "Descripción",
            "performed_at": "Fecha de realización",
            "completed_at": "Fecha de término",
            "next_maintenance": "Próximo mantenimiento",
            "status": "Estado",
            "notes": "Notas",
        }

    client_rut = forms.CharField(
        label="RUT del cliente",
        max_length=20,
        widget=forms.TextInput(attrs={"data-rut": "true", "autocomplete": "off"}),
    )
    performed_by = forms.ModelChoiceField(
        label="Responsable del mantenimiento",
        queryset=User.objects.none(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment"].queryset = Equipment.objects.exclude(
            status=Equipment.Status.RETIRED
        )
        self.fields["performed_by"].queryset = User.objects.filter(is_active=True)
        if self.instance.pk and self.instance.work_order_id:
            self.initial["client_rut"] = self.instance.work_order.client_rut
        self.fields["status"].choices = [
            choice
            for choice in MaintenanceRecord.Status.choices
            if choice[0] != MaintenanceRecord.Status.COMPLETED
        ]

    def clean_client_rut(self):
        return normalize_rut(self.cleaned_data["client_rut"])
