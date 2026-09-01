from django import forms

from .models import Equipment


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            "name",
            "code",
            "description",
            "serial_number",
            "brand",
            "model",
            "location",
            "commissioned_at",
            "application",
            "status",
        ]
        labels = {
            "name": "Nombre",
            "code": "Código",
            "description": "Descripción",
            "serial_number": "Número de serie",
            "brand": "Marca",
            "model": "Modelo",
            "location": "Ubicación",
            "commissioned_at": "Fecha de puesta en servicio",
            "application": "Aplicación",
            "status": "Estado",
        }
        widgets = {"commissioned_at": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            choice
            for choice in Equipment.Status.choices
            if choice[0] != Equipment.Status.RETIRED
        ]
