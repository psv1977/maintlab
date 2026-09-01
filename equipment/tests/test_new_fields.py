import pytest
from django.contrib.auth.models import User

from equipment.forms import EquipmentForm
from equipment.models import Equipment, Location


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.mark.django_db
def test_equipment_stores_new_fields(user):
    location = Location.objects.create(name="Planta norte")
    equipment = Equipment.objects.create(
        name="Bomba",
        code="BOM-001",
        brand="Acme",
        model="X1",
        location=location,
        commissioned_at="2026-01-15",
        application="Agua industrial",
        created_by=user,
    )

    assert equipment.location == location
    assert equipment.brand == "Acme"
    assert equipment.model == "X1"
    assert str(equipment.commissioned_at) == "2026-01-15"
    assert equipment.application == "Agua industrial"


@pytest.mark.django_db
def test_equipment_form_includes_new_fields():
    form = EquipmentForm()
    assert {"brand", "model", "location", "commissioned_at", "application"}.issubset(
        form.fields
    )
