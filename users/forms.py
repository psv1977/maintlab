from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth.models import User


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
