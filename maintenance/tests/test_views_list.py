import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from equipment.models import Equipment
from maintenance.models import MaintenanceRecord


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.fixture
def equipment(user):
    return Equipment.objects.create(
        name="Compresor principal",
        code="COMP-001",
        created_by=user,
    )


@pytest.fixture
def maintenance_record(user, equipment):
    return MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type=MaintenanceRecord.MaintenanceType.SCHEDULED,
        description="Cambio de aceite",
        performed_by=user,
        performed_at=timezone.now(),
        created_by=user,
    )


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_login(client):
    response = client.get(reverse("maintenance:list"))
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_authenticated_user_sees_maintenance_list(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:list"))
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]


@pytest.mark.django_db
def test_authenticated_user_sees_maintenance_detail(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:detail", args=[maintenance_record.pk]))
    assert response.status_code == 200
    assert response.context["maintenance_record"] == maintenance_record


@pytest.mark.django_db
def test_anonymous_user_is_redirected_from_detail(client, maintenance_record):
    response = client.get(reverse("maintenance:detail", args=[maintenance_record.pk]))
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_maintenance_list_is_paginated_by_twenty(client, user):
    equipment = Equipment.objects.create(
        name="Equipo de prueba",
        code="EQ-TEST",
        created_by=user,
    )
    MaintenanceRecord.objects.bulk_create(
        [
            MaintenanceRecord(
                equipment=equipment,
                maintenance_type=MaintenanceRecord.MaintenanceType.SCHEDULED,
                description=f"Mantenimiento {number:02}",
                performed_by=user,
                performed_at=timezone.now(),
                created_by=user,
            )
            for number in range(1, 22)
        ]
    )
    client.force_login(user)

    first_page = client.get(reverse("maintenance:list"))
    second_page = client.get(reverse("maintenance:list"), {"page": 2})

    assert first_page.status_code == 200
    assert first_page.context["paginator"].num_pages == 2
    assert len(first_page.context["maintenance_records"]) == 20
    assert second_page.status_code == 200
    assert len(second_page.context["maintenance_records"]) == 1
