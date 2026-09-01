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
        description="Cambio de aceite programado",
        performed_by=user,
        performed_at=timezone.now(),
        created_by=user,
    )


@pytest.mark.django_db
def test_search_by_description(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:list"), {"q": "aceite"})
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]


@pytest.mark.django_db
def test_search_by_equipment_name(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:list"), {"q": "Compresor"})
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]


@pytest.mark.django_db
def test_search_by_equipment_code(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:list"), {"q": "COMP-001"})
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]


@pytest.mark.django_db
def test_filter_by_type(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:list"), {"type": "scheduled"})
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]


@pytest.mark.django_db
def test_filter_by_status(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:list"), {"status": "pending"})
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]


@pytest.mark.django_db
def test_filter_by_invalid_type_returns_all(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:list"), {"type": "invalid"})
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]


@pytest.mark.django_db
def test_filter_by_invalid_status_returns_all(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:list"), {"status": "invalid"})
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]


@pytest.mark.django_db
def test_combined_search_and_filter(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(
        reverse("maintenance:list"),
        {"q": "aceite", "type": "scheduled", "status": "pending"},
    )
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]


@pytest.mark.django_db
def test_search_no_results(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:list"), {"q": "nonexistent"})
    assert response.status_code == 200
    assert maintenance_record not in response.context["maintenance_records"]
