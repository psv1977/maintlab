import pytest
from django.contrib.auth.models import User

from equipment.forms import EquipmentForm
from equipment.models import Equipment


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


def form_data(**overrides):
    data = {
        "name": "Compresor principal",
        "code": "COMP-001",
        "description": "Compresor de la línea principal",
        "serial_number": "SN-001",
        "status": Equipment.Status.OPERATIONAL,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_valid_equipment_form(user):
    form = EquipmentForm(data=form_data())

    assert form.is_valid()


@pytest.mark.django_db
def test_name_and_code_are_required(user):
    form_without_name = EquipmentForm(data=form_data(name=""))
    form_without_code = EquipmentForm(data=form_data(code=""))

    assert not form_without_name.is_valid()
    assert "name" in form_without_name.errors
    assert not form_without_code.is_valid()
    assert "code" in form_without_code.errors


@pytest.mark.django_db
def test_duplicate_code_is_rejected(user):
    Equipment.objects.create(
        name="Equipo existente",
        code="COMP-001",
        created_by=user,
    )

    form = EquipmentForm(data=form_data())

    assert not form.is_valid()
    assert "code" in form.errors


@pytest.mark.django_db
def test_description_and_serial_number_are_optional(user):
    form = EquipmentForm(data=form_data(description="", serial_number=""))

    assert form.is_valid()


@pytest.mark.django_db
def test_retired_is_not_an_available_status(user):
    form = EquipmentForm(data=form_data(status=Equipment.Status.RETIRED))

    assert Equipment.Status.RETIRED not in dict(form.fields["status"].choices)
    assert not form.is_valid()
    assert "status" in form.errors


@pytest.mark.django_db
def test_unknown_status_is_rejected(user):
    form = EquipmentForm(data=form_data(status="unknown"))

    assert not form.is_valid()
    assert "status" in form.errors
