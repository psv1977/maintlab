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


@pytest.mark.django_db
def test_create_view_requires_login(client):
    response = client.get(reverse("maintenance:create"))
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_create_view_get(client, user):
    client.force_login(user)
    response = client.get(reverse("maintenance:create"))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_create_view_post_valid(client, user, equipment):
    client.force_login(user)
    data = {
        "equipment": equipment.pk,
        "client_rut": "11.111.111-1",
        "maintenance_type": "scheduled",
        "description": "Cambio de aceite",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
    }
    response = client.post(reverse("maintenance:create"), data)
    assert response.status_code == 302
    assert response.url == reverse("maintenance:list")

    record = MaintenanceRecord.objects.get(description="Cambio de aceite")
    assert record.equipment == equipment
    assert record.maintenance_type == "scheduled"
    assert record.status == "pending"
    assert record.created_by == user
    assert record.performed_by == user


@pytest.mark.django_db
def test_create_view_post_invalid(client, user, equipment):
    client.force_login(user)
    data = {
        "equipment": equipment.pk,
        "client_rut": "11.111.111-1",
        "maintenance_type": "scheduled",
        "description": "",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
    }
    response = client.post(reverse("maintenance:create"), data)
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_create_view_sets_created_by(client, user, equipment):
    client.force_login(user)
    data = {
        "equipment": equipment.pk,
        "client_rut": "11.111.111-1",
        "maintenance_type": "scheduled",
        "description": "Cambio de aceite",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
    }
    client.post(reverse("maintenance:create"), data)
    record = MaintenanceRecord.objects.get(description="Cambio de aceite")
    assert record.created_by == user
    assert record.created_at is not None


@pytest.mark.django_db
def test_create_view_sets_performed_by(client, user, equipment):
    client.force_login(user)
    data = {
        "equipment": equipment.pk,
        "client_rut": "11.111.111-1",
        "maintenance_type": "scheduled",
        "description": "Cambio de aceite",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
    }
    client.post(reverse("maintenance:create"), data)
    record = MaintenanceRecord.objects.get(description="Cambio de aceite")
    assert record.performed_by == user
