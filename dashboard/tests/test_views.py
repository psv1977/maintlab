from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from equipment.models import Equipment
from maintenance.models import MaintenanceRecord, WorkOrder


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
def maintenance(user, equipment):
    return MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type="scheduled",
        description="Mantenimiento preventivo",
        performed_by=user,
        performed_at=timezone.now(),
        created_by=user,
    )


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_login(client):
    response = client.get(reverse("dashboard:index"))

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")
    assert "next=" in response.url


@pytest.mark.django_db
def test_authenticated_user_can_access_dashboard(client, user):
    client.force_login(user)

    response = client.get(reverse("dashboard:index"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_context_contains_expected_keys(client, user):
    client.force_login(user)

    response = client.get(reverse("dashboard:index"))

    assert "equipment_by_status" in response.context
    assert "maintenance_by_status" in response.context
    assert "total_work_orders" in response.context
    assert "recent_equipments" in response.context
    assert "recent_maintenances" in response.context
    assert "upcoming_maintenances" in response.context


@pytest.mark.django_db
def test_dashboard_equipment_counts_are_correct(client, user, equipment):
    client.force_login(user)

    response = client.get(reverse("dashboard:index"))

    equipment_by_status = response.context["equipment_by_status"]
    assert equipment_by_status["operational"]["count"] == 1
    assert equipment_by_status["in_maintenance"]["count"] == 0
    assert equipment_by_status["out_of_service"]["count"] == 0
    assert equipment_by_status["retired"]["count"] == 0


@pytest.mark.django_db
def test_dashboard_maintenance_counts_are_correct(client, user, maintenance):
    client.force_login(user)

    response = client.get(reverse("dashboard:index"))

    maintenance_by_status = response.context["maintenance_by_status"]
    assert maintenance_by_status["pending"]["count"] == 1
    assert maintenance_by_status["in_progress"]["count"] == 0
    assert maintenance_by_status["completed"]["count"] == 0


@pytest.mark.django_db
def test_dashboard_upcoming_maintenances_only_next_30_days(client, user, equipment):
    client.force_login(user)

    # Mantenimiento dentro de 15 días (debe aparecer)
    MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type="scheduled",
        description="Mantenimiento futuro cercano",
        performed_by=user,
        performed_at=timezone.now(),
        next_maintenance=timezone.now() + timedelta(days=15),
        created_by=user,
    )

    # Mantenimiento dentro de 60 días (no debe aparecer)
    MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type="scheduled",
        description="Mantenimiento futuro lejano",
        performed_by=user,
        performed_at=timezone.now(),
        next_maintenance=timezone.now() + timedelta(days=60),
        created_by=user,
    )

    response = client.get(reverse("dashboard:index"))

    upcoming = response.context["upcoming_maintenances"]
    assert len(upcoming) == 1
    assert upcoming[0].description == "Mantenimiento futuro cercano"


@pytest.mark.django_db
def test_dashboard_total_work_orders(client, user, equipment):
    client.force_login(user)

    WorkOrder.objects.create(
        number="OT-0001",
        client_rut="12345678-9",
        equipment=equipment,
        created_by=user,
    )
    WorkOrder.objects.create(
        number="OT-0002",
        client_rut="98765432-1",
        equipment=equipment,
        created_by=user,
    )

    response = client.get(reverse("dashboard:index"))

    assert response.context["total_work_orders"] == 2


@pytest.mark.django_db
def test_dashboard_recent_equipments_ordered_by_created_at(client, user):
    client.force_login(user)

    eq1 = Equipment.objects.create(
        name="Equipo antiguo",
        code="EQ-001",
        created_by=user,
    )
    eq2 = Equipment.objects.create(
        name="Equipo nuevo",
        code="EQ-002",
        created_by=user,
    )

    response = client.get(reverse("dashboard:index"))

    recent = list(response.context["recent_equipments"])
    assert len(recent) == 2
    # El más reciente primero
    assert recent[0].pk == eq2.pk
    assert recent[1].pk == eq1.pk
