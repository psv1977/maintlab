import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse

from equipment.models import Equipment, EquipmentIdentifier


pytestmark = pytest.mark.django_db


def test_identifier_is_assigned_to_equipment_and_organization(client):
    user = User.objects.create_user(username="identifier-user")
    equipment = Equipment.objects.create(name="Vehículo", code="VH-001", created_by=user)
    client.force_login(user)

    response = client.post(
        reverse("equipment:identifier-create", args=[equipment.pk]),
        {"identifier_type": "license_plate", "value": "ABCD12"},
    )

    identifier = EquipmentIdentifier.objects.get()
    assert response.status_code == 302
    assert identifier.equipment == equipment
    assert identifier.organization == equipment.organization


def test_identifier_value_is_unique_per_type_and_organization():
    user = User.objects.create_user(username="identifier-unique-user")
    first = Equipment.objects.create(name="Uno", code="ONE", created_by=user)
    second = Equipment.objects.create(name="Dos", code="TWO", created_by=user)
    EquipmentIdentifier.objects.create(
        organization=first.organization, equipment=first, identifier_type="vin", value="VIN-1",
    )

    with pytest.raises(IntegrityError):
        EquipmentIdentifier.objects.create(
            organization=second.organization, equipment=second, identifier_type="vin", value="VIN-1",
        )
