import pytest
from django.contrib.auth.models import User

from users.forms import UserCreateForm, UserForm, UserGroupsForm


@pytest.mark.django_db
def test_user_form_valid():
    data = {
        "username": "tecnico",
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan@test.com",
        "is_active": True,
        "is_staff": False,
    }
    form = UserForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_user_form_required_fields():
    form = UserForm(data={})
    assert not form.is_valid()
    assert "username" in form.errors


@pytest.mark.django_db
def test_user_form_optional_fields():
    data = {
        "username": "tecnico",
        "first_name": "",
        "last_name": "",
        "email": "",
        "is_active": True,
        "is_staff": False,
    }
    form = UserForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_user_create_form_valid():
    data = {
        "username": "tecnico",
        "password1": "testpass123!",
        "password2": "testpass123!",
    }
    form = UserCreateForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_user_create_form_password_mismatch():
    data = {
        "username": "tecnico",
        "password1": "testpass123!",
        "password2": "differentpass",
    }
    form = UserCreateForm(data=data)
    assert not form.is_valid()
    assert "password2" in form.errors


@pytest.mark.django_db
def test_user_groups_form_initial():
    from django.contrib.auth.models import Group
    user = User.objects.create_user(username="tecnico", password="test1234")
    group, _ = Group.objects.get_or_create(name="tecnicos")
    user.groups.add(group)

    form = UserGroupsForm(user=user)
    assert list(form.initial["groups"]) == [group.pk]
