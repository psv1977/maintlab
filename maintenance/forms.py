from django import forms
from equipment.models import Equipment

from .models import MaintenancePlan, MaintenanceRecord
from .rut import normalize_rut


class MaintenanceForm(forms.ModelForm):
    reset_plans = forms.ModelMultipleChoiceField(
        label="Planes que cumple este mantenimiento",
        queryset=MaintenancePlan.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = MaintenanceRecord
        fields = [
            "equipment",
            "client_rut",
            "maintenance_type",
            "description",
            "meter_reading",
            "performed_at",
            "completed_at",
            "next_maintenance",
            "status",
            "notes",
            "reset_plans",
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
            "meter_reading": "Lectura actual",
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
    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment"].queryset = Equipment.objects.exclude(
            status=Equipment.Status.RETIRED
        )
        if organization:
            self.fields["equipment"].queryset = self.fields["equipment"].queryset.filter(organization=organization)
            self.fields["reset_plans"].queryset = MaintenancePlan.objects.filter(
                organization=organization, active=True
            ).select_related("equipment")
        if self.instance.pk and self.instance.work_order_id:
            self.initial["client_rut"] = self.instance.work_order.client_rut
        equipment = self.instance.equipment if self.instance.pk else None
        if not equipment and self.data.get("equipment"):
            equipment = Equipment.objects.filter(pk=self.data.get("equipment")).first()
        if equipment:
            self.fields["meter_reading"].label = equipment.measurement_unit_label
        self.fields["status"].choices = [
            choice
            for choice in MaintenanceRecord.Status.choices
            if choice[0] != MaintenanceRecord.Status.COMPLETED
        ]

    def clean_client_rut(self):
        return normalize_rut(self.cleaned_data["client_rut"])

    def clean(self):
        cleaned_data = super().clean()
        equipment = cleaned_data.get("equipment")
        meter_reading = cleaned_data.get("meter_reading")
        reset_plans = cleaned_data.get("reset_plans")
        if meter_reading is not None and meter_reading < 0:
            self.add_error("meter_reading", "La lectura no puede ser negativa.")
        if equipment and reset_plans:
            invalid_plans = [plan for plan in reset_plans if plan.equipment_id != equipment.pk]
            if invalid_plans:
                self.add_error(
                    "reset_plans",
                    "Los planes seleccionados deben pertenecer al equipo elegido.",
                )
            if any(plan.strategy == MaintenancePlan.Strategy.METER for plan in reset_plans) and meter_reading is None:
                self.add_error("meter_reading", "Indique la lectura para reiniciar un plan por uso.")
        return cleaned_data


class MaintenancePlanForm(forms.ModelForm):
    class Meta:
        model = MaintenancePlan
        fields = ["equipment", "name", "strategy", "interval_days", "interval_value", "active"]
        labels = {
            "equipment": "Equipo",
            "name": "Nombre del plan",
            "strategy": "Estrategia",
            "interval_days": "Intervalo en días",
            "interval_value": "Intervalo de uso",
            "active": "Plan activo",
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization
        self.fields["equipment"].queryset = Equipment.objects.exclude(
            status=Equipment.Status.RETIRED
        )
        if organization:
            self.fields["equipment"].queryset = self.fields["equipment"].queryset.filter(
                organization=organization
            )
            self.instance.organization = organization

    def clean(self):
        cleaned_data = super().clean()
        strategy = cleaned_data.get("strategy")
        if strategy == MaintenancePlan.Strategy.TIME:
            cleaned_data["interval_value"] = None
        elif strategy == MaintenancePlan.Strategy.METER:
            cleaned_data["interval_days"] = None
        return cleaned_data
