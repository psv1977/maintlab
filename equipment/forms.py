from django import forms

from organizations.models import default_organization

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

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization_id = organization.pk if organization else self.instance.organization_id or default_organization()
        if organization:
            self.fields["location"].queryset = self.fields["location"].queryset.filter(organization=organization)
        self.fields["status"].choices = [
            choice
            for choice in Equipment.Status.choices
            if choice[0] != Equipment.Status.RETIRED
        ]

    def clean_code(self):
        code = self.cleaned_data["code"]
        queryset = Equipment.objects.filter(organization_id=self.organization_id, code=code)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Ya existe un equipo con este código en la empresa.")
        return code


class EquipmentImportForm(forms.Form):
    file = forms.FileField(label="Planilla Excel")

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if not uploaded_file.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("Seleccione un archivo Excel con extensión .xlsx.")
        return uploaded_file
