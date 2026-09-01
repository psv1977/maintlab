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
def test_update_view_requires_login(client, maintenance_record):
    response = client.get(reverse("maintenance:update", args=[maintenance_record.pk]))
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_update_view_get(client, user, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:update", args=[maintenance_record.pk]))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_update_view_post_valid(client, user, maintenance_record):
    client.force_login(user)
    data = {
        "equipment": maintenance_record.equipment.pk,
        "maintenance_type": "unscheduled",
        "description": "Reparación de emergencia",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "in_progress",
    }
    response = client.post(reverse("maintenance:update", args=[maintenance_record.pk]), data)
    assert response.status_code == 302
    assert response.url == reverse("maintenance:detail", args=[maintenance_record.pk])

    maintenance_record.refresh_from_db()
    assert maintenance_record.description == "Reparación de emergencia"
    assert maintenance_record.status == "in_progress"
    assert maintenance_record.updated_by == user
    assert maintenance_record.updated_at is not None


@pytest.mark.django_db
def test_update_view_post_invalid(client, user, maintenance_record):
    client.force_login(user)
    data = {
        "equipment": maintenance_record.equipment.pk,
        "maintenance_type": "scheduled",
        "description": "",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
    }
    response = client.post(reverse("maintenance:update", args=[maintenance_record.pk]), data)
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_update_view_sets_updated_by(client, user, maintenance_record):
    client.force_login(user)
    data = {
        "equipment": maintenance_record.equipment.pk,
        "maintenance_type": "scheduled",
        "description": "Cambio de aceite actualizado",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
    }
    client.post(reverse("maintenance:update", args=[maintenance_record.pk]), data)
    maintenance_record.refresh_from_db()
    assert maintenance_record.updated_by == user
    assert maintenance_record.updated_at is not None


@pytest.mark.django_db
def test_update_view_preserves_created_by(client, user, maintenance_record):
    client.force_login(user)
    data = {
        "equipment": maintenance_record.equipment.pk,
        "maintenance_type": "scheduled",
        "description": "Cambio de aceite actualizado",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
    }
    client.post(reverse("maintenance:update", args=[maintenance_record.pk]), data)
    maintenance_record.refresh_from_db()
    assert maintenance_record.created_by == user
    assert maintenance_record.created_at is not None
