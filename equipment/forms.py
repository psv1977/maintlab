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
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            choice
            for choice in Equipment.Status.choices
            if choice[0] != Equipment.Status.RETIRED
        ]
