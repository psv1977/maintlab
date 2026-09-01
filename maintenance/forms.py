from django import forms

from equipment.models import Equipment

from .models import MaintenanceRecord


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            "equipment",
            "maintenance_type",
            "description",
            "performed_at",
            "next_maintenance",
            "status",
            "notes",
        ]
        widgets = {
            "performed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "next_maintenance": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment"].queryset = Equipment.objects.exclude(
            status=Equipment.Status.RETIRED
        )
        self.fields["status"].choices = [
            choice
            for choice in MaintenanceRecord.Status.choices
            if choice[0] != MaintenanceRecord.Status.COMPLETED
        ]
