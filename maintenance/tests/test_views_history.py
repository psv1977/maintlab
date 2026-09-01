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
def test_history_view_requires_login(client, equipment):
    response = client.get(reverse("maintenance:history", args=[equipment.pk]))
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_history_view_get(client, user, equipment, maintenance_record):
    client.force_login(user)
    response = client.get(reverse("maintenance:history", args=[equipment.pk]))
    assert response.status_code == 200
    assert maintenance_record in response.context["maintenance_records"]
    assert response.context["equipment"] == equipment


@pytest.mark.django_db
def test_history_view_404_for_nonexistent_equipment(client, user):
    client.force_login(user)
    response = client.get(reverse("maintenance:history", args=[99999]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_history_view_only_shows_equipment_records(client, user, equipment):
    client.force_login(user)
    other_equipment = Equipment.objects.create(
        name="Otro equipo",
        code="OTHER-001",
        created_by=user,
    )
    record1 = MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type=MaintenanceRecord.MaintenanceType.SCHEDULED,
        description="Mantenimiento equipo 1",
        performed_by=user,
        performed_at=timezone.now(),
        created_by=user,
    )
    record2 = MaintenanceRecord.objects.create(
        equipment=other_equipment,
        maintenance_type=MaintenanceRecord.MaintenanceType.UNSCHEDULED,
        description="Mantenimiento equipo 2",
        performed_by=user,
        performed_at=timezone.now(),
        created_by=user,
    )

    response = client.get(reverse("maintenance:history", args=[equipment.pk]))
    assert response.status_code == 200
    assert record1 in response.context["maintenance_records"]
    assert record2 not in response.context["maintenance_records"]
