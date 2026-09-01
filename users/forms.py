from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
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
