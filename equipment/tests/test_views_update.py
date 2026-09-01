import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from equipment.models import Equipment


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.fixture
def equipment(user):
    return Equipment.objects.create(
        name="Compresor principal",
        code="COMP-001",
        description="Compresor de la línea principal",
        serial_number="SN-001",
        created_by=user,
    )


def form_data(**overrides):
    data = {
        "name": "Compresor actualizado",
        "code": "COMP-002",
        "description": "Nueva descripción",
        "serial_number": "SN-002",
        "status": Equipment.Status.IN_MAINTENANCE,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_valid_edit_persists_changes(client, user, equipment):
    client.force_login(user)

    response = client.post(
        reverse("equipment:update", args=[equipment.pk]),
        form_data(),
    )

    assert response.status_code == 302
    assert response.url == reverse("equipment:detail", args=[equipment.pk])
    equipment.refresh_from_db()
    assert equipment.name == "Compresor actualizado"
    assert equipment.code == "COMP-002"
    assert equipment.description == "Nueva descripción"
    assert equipment.serial_number == "SN-002"
    assert equipment.status == Equipment.Status.IN_MAINTENANCE


@pytest.mark.django_db
def test_first_edit_sets_updated_by_and_updated_at(client, user, equipment):
    client.force_login(user)

    client.post(reverse("equipment:update", args=[equipment.pk]), form_data())

    equipment.refresh_from_db()
    assert equipment.updated_by == user
    assert equipment.updated_at is not None


@pytest.mark.django_db
def test_second_edit_refreshes_updated_fields(client, user, equipment):
    client.force_login(user)

    client.post(reverse("equipment:update", args=[equipment.pk]), form_data())
    equipment.refresh_from_db()
    first_updated_at = equipment.updated_at

    client.post(
        reverse("equipment:update", args=[equipment.pk]),
        form_data(name="Segunda edición", code="COMP-003"),
    )
    equipment.refresh_from_db()
    assert equipment.updated_at > first_updated_at
    assert equipment.name == "Segunda edición"
    assert equipment.code == "COMP-003"


@pytest.mark.django_db
def test_duplicate_code_of_other_equipment_is_rejected(client, user, equipment):
    other = Equipment.objects.create(
        name="Otro equipo", code="OTHER-001", created_by=user
    )
    client.force_login(user)

    response = client.post(
        reverse("equipment:update", args=[equipment.pk]),
        form_data(code="OTHER-001"),
    )

    assert response.status_code == 200
    equipment.refresh_from_db()
    assert equipment.code == "COMP-001"


@pytest.mark.django_db
def test_own_code_is_accepted(client, user, equipment):
    client.force_login(user)

    response = client.post(
        reverse("equipment:update", args=[equipment.pk]),
        form_data(code="COMP-001"),
    )

    assert response.status_code == 302
    equipment.refresh_from_db()
    assert equipment.code == "COMP-001"


@pytest.mark.django_db
def test_retired_status_is_rejected(client, user, equipment):
    client.force_login(user)

    response = client.post(
        reverse("equipment:update", args=[equipment.pk]),
        form_data(status=Equipment.Status.RETIRED),
    )

    assert response.status_code == 200
    equipment.refresh_from_db()
    assert equipment.status == Equipment.Status.OPERATIONAL


@pytest.mark.django_db
def test_operational_transitions_are_allowed(client, user, equipment):
    client.force_login(user)

    for status in [
        Equipment.Status.IN_MAINTENANCE,
        Equipment.Status.OUT_OF_SERVICE,
        Equipment.Status.OPERATIONAL,
    ]:
        response = client.post(
            reverse("equipment:update", args=[equipment.pk]),
            form_data(status=status),
        )
        assert response.status_code == 302
        equipment.refresh_from_db()
        assert equipment.status == status


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_login(client, equipment):
    response = client.get(reverse("equipment:update", args=[equipment.pk]))

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")
