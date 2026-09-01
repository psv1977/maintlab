import pytest
from django.contrib.auth.models import User
from django.urls import reverse

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
def test_valid_post_creates_equipment(client, user):
    client.force_login(user)

    response = client.post(reverse("equipment:create"), form_data())

    assert response.status_code == 302
    assert response.url == reverse("equipment:list")
    assert Equipment.objects.count() == 1
    equipment = Equipment.objects.first()
    assert equipment.name == "Compresor principal"
    assert equipment.code == "COMP-001"
    assert equipment.description == "Compresor de la línea principal"
    assert equipment.serial_number == "SN-001"
    assert equipment.status == Equipment.Status.OPERATIONAL
    assert equipment.created_by == user
    assert equipment.created_at is not None
    assert equipment.updated_by is None
    assert equipment.updated_at is None


@pytest.mark.django_db
def test_missing_name_is_rejected(client, user):
    client.force_login(user)

    response = client.post(reverse("equipment:create"), form_data(name=""))

    assert response.status_code == 200
    assert Equipment.objects.count() == 0


@pytest.mark.django_db
def test_missing_code_is_rejected(client, user):
    client.force_login(user)

    response = client.post(reverse("equipment:create"), form_data(code=""))

    assert response.status_code == 200
    assert Equipment.objects.count() == 0


@pytest.mark.django_db
def test_duplicate_code_is_rejected(client, user):
    Equipment.objects.create(
        name="Equipo existente", code="COMP-001", created_by=user
    )
    client.force_login(user)

    response = client.post(reverse("equipment:create"), form_data())

    assert response.status_code == 200
    assert Equipment.objects.count() == 1


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_login(client):
    response = client.post(reverse("equipment:create"), form_data())

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_successful_create_redirects_to_list(client, user):
    client.force_login(user)

    response = client.post(reverse("equipment:create"), form_data())

    assert response.status_code == 302
    assert response.url == reverse("equipment:list")


@pytest.mark.django_db
def test_status_is_always_operational_on_create(client, user):
    client.force_login(user)

    response = client.post(
        reverse("equipment:create"),
        form_data(status=Equipment.Status.IN_MAINTENANCE),
    )

    assert response.status_code == 302
    equipment = Equipment.objects.first()
    assert equipment.status == Equipment.Status.OPERATIONAL


@pytest.mark.django_db
def test_status_retired_cannot_be_submitted(client, user):
    client.force_login(user)

    response = client.post(
        reverse("equipment:create"),
        form_data(status=Equipment.Status.RETIRED),
    )

    assert response.status_code == 200
    assert Equipment.objects.count() == 0
