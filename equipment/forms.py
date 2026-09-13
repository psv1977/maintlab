from django import forms

from organizations.models import Customer, default_organization

from .models import Equipment, EquipmentIdentifier, Location, MeterReading


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            "name",
            "customer",
            "code",
            "equipment_type",
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
            "customer": "Cliente o propietario",
            "code": "Código",
            "equipment_type": "Tipo de equipo",
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
        self.fields["equipment_type"].required = False
        self.initial.setdefault("equipment_type", Equipment.EquipmentType.INDUSTRIAL)
        self.organization_id = organization.pk if organization else self.instance.organization_id or default_organization()
        if organization:
            self.fields["location"].queryset = self.fields["location"].queryset.filter(organization=organization)
            self.fields["customer"].queryset = Customer.objects.filter(organization=organization)
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


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "description"]
        labels = {
            "name": "Nombre",
            "description": "Descripción",
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        if organization:
            self.instance.organization = organization


class MeterReadingForm(forms.ModelForm):
    class Meta:
        model = MeterReading
        fields = ["value", "recorded_at", "notes"]
        labels = {
            "value": "Lectura",
            "recorded_at": "Fecha de lectura",
            "notes": "Observaciones",
        }
        widgets = {
            "recorded_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, equipment=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.equipment = equipment
        if equipment:
            self.fields["value"].label = equipment.measurement_unit_label

    def clean_value(self):
        value = self.cleaned_data["value"]
        if value < 0:
            raise forms.ValidationError("La lectura no puede ser negativa.")
        if self.equipment:
            last_reading = self.equipment.meter_readings.order_by("-recorded_at", "-pk").first()
            if last_reading and value < last_reading.value:
                raise forms.ValidationError(
                    "La lectura no puede ser menor que la última lectura registrada."
                )
        return value


class EquipmentIdentifierForm(forms.ModelForm):
    class Meta:
        model = EquipmentIdentifier
        fields = ["identifier_type", "value"]
        labels = {"identifier_type": "Tipo de identificador", "value": "Valor"}


class EquipmentImportForm(forms.Form):
    file = forms.FileField(label="Planilla Excel")

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if not uploaded_file.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("Seleccione un archivo Excel con extensión .xlsx.")
        return uploaded_file
