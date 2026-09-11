from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth.models import User

from maintenance.rut import normalize_rut
from organizations.models import Comuna, Organization, OrganizationInvitation, Region


class UserForm(forms.ModelForm):
    def __init__(self, *args, can_manage_staff=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not can_manage_staff:
            self.fields.pop("is_staff", None)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["first_name"].label = "Nombre"
        self.fields["last_name"].label = "Apellido"
        self.fields["email"].label = "Correo electrónico"
        self.fields["is_active"].label = "Usuario activo"
        if "is_staff" in self.fields:
            self.fields["is_staff"].label = "Acceso administrativo (staff)"

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
        ]


class UserCreateForm(UserCreationForm):
    def __init__(self, *args, can_manage_staff=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not can_manage_staff:
            self.fields.pop("is_staff", None)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["first_name"].label = "Nombre"
        self.fields["last_name"].label = "Apellido"
        self.fields["email"].label = "Correo electrónico"
        self.fields["is_active"].label = "Usuario activo"
        if "is_staff" in self.fields:
            self.fields["is_staff"].label = "Acceso administrativo (staff)"

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
        ]


class UserGroupsForm(forms.Form):
    groups = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, user=None, **kwargs):
        kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import Group
        self.fields["groups"].choices = [
            (group.pk, group.name) for group in Group.objects.all()
        ]
        if user:
            self.initial["groups"] = list(user.groups.values_list("pk", flat=True))


class UserPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput,
    )


class OrganizationRutForm(forms.Form):
    rut = forms.CharField(
        label="RUT de la empresa",
        widget=forms.TextInput(attrs={"data-rut": "true", "autocomplete": "off"}),
    )

    def clean_rut(self):
        return normalize_rut(self.cleaned_data["rut"])


class OrganizationRegistrationForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        label="Región",
        empty_label="-- Seleccionar región --",
    )
    comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.none(),
        label="Comuna",
        empty_label="-- Seleccionar comuna --",
    )

    class Meta:
        model = Organization
        fields = ["name", "rut", "business_line", "region", "comuna", "address"]
        labels = {
            "name": "Razón social",
            "rut": "RUT de la empresa",
            "business_line": "Giro",
            "address": "Dirección",
        }
        widgets = {
            "rut": forms.TextInput(attrs={"data-rut": "true", "autocomplete": "off"}),
            "region": forms.Select(attrs={"data-comunas-url": "/users/api/comunas/"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["region"].widget.attrs.update({"data-comunas-url": "/users/api/comunas/"})
        if self.data.get("region"):
            try:
                region_id = int(self.data.get("region"))
                self.fields["comuna"].queryset = Comuna.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get("region")
        comuna = cleaned_data.get("comuna")
        if region and comuna and comuna.region != region:
            self.add_error("comuna", "La comuna seleccionada no pertenece a la región elegida.")
        return cleaned_data

    def clean_rut(self):
        value = self.cleaned_data.get("rut")
        if not value:
            return value
        return normalize_rut(value)


class PublicUserRegistrationForm(UserCreationForm):
    invitation_code = forms.CharField(label="Código de invitación", required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def __init__(self, *args, organization=None, requires_invitation=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization
        self.requires_invitation = requires_invitation
        self.fields["username"].label = "Nombre de usuario"
        self.fields["first_name"].label = "Nombre"
        self.fields["last_name"].label = "Apellido"
        self.fields["email"].label = "Correo electrónico"
        self.fields["invitation_code"].required = requires_invitation
        if not requires_invitation:
            self.fields.pop("invitation_code")

    def clean_invitation_code(self):
        code = self.cleaned_data["invitation_code"].strip()
        if not OrganizationInvitation.objects.filter(organization=self.organization, code=code).exists():
            raise forms.ValidationError("El código de invitación no es válido para esta empresa.")
        return code
