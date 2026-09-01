import pytest
from django.contrib.auth.models import User
from django.urls import reverse

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


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_login(client):
    response = client.get(reverse("equipment:list"))

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")
    assert "next=" in response.url


@pytest.mark.django_db
def test_authenticated_user_sees_equipment_list(client, user, equipment):
    client.force_login(user)

    response = client.get(reverse("equipment:list"))

    assert response.status_code == 200
    assert list(response.context["equipments"]) == [equipment]
    assert equipment.name.encode() in response.content


@pytest.mark.django_db
def test_authenticated_user_sees_equipment_detail(client, user, equipment):
    client.force_login(user)

    response = client.get(reverse("equipment:detail", args=[equipment.pk]))

    assert response.status_code == 200
    assert response.context["equipment"] == equipment
    assert equipment.name.encode() in response.content
    assert equipment.code.encode() in response.content
    assert equipment.description.encode() in response.content
    assert equipment.serial_number.encode() in response.content
    assert b"Operativo" in response.content


@pytest.mark.django_db
def test_anonymous_user_is_redirected_from_detail(client, equipment):
    response = client.get(reverse("equipment:detail", args=[equipment.pk]))

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_equipment_list_is_paginated_by_twenty(client, user):
    Equipment.objects.bulk_create(
        [
            Equipment(name=f"Equipo {number:02}", code=f"EQ-{number:02}", created_by=user)
            for number in range(1, 22)
        ]
    )
    client.force_login(user)

    first_page = client.get(reverse("equipment:list"))
    second_page = client.get(reverse("equipment:list"), {"page": 2})

    assert first_page.status_code == 200
    assert first_page.context["paginator"].num_pages == 2
    assert len(first_page.context["equipments"]) == 20
    assert second_page.status_code == 200
    assert len(second_page.context["equipments"]) == 1


@pytest.mark.django_db
def test_retired_equipment_remains_in_list(client, user):
    retired = Equipment.objects.create(
        name="Equipo retirado",
        code="RET-001",
        status=Equipment.Status.RETIRED,
        created_by=user,
    )
    client.force_login(user)

    response = client.get(reverse("equipment:list"))

    assert response.status_code == 200
    assert retired in response.context["equipments"]
    assert retired.name.encode() in response.content
