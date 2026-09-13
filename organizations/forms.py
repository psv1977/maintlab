from django import forms

from .models import Customer
from .rut import normalize_rut


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["rut", "name", "customer_type"]
        labels = {"rut": "RUT", "name": "Nombre o razón social", "customer_type": "Tipo de cliente"}
        widgets = {"rut": forms.TextInput(attrs={"data-rut": "true", "autocomplete": "off"})}

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization

    def clean_rut(self):
        rut = normalize_rut(self.cleaned_data["rut"])
        queryset = Customer.objects.filter(organization=self.organization, rut=rut)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Ya existe un cliente con este RUT en la empresa.")
        return rut
