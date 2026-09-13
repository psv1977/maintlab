from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from equipment.models import Equipment, Location, MeterReading
from maintenance.models import MaintenancePlan, MaintenanceRecord, WorkOrder
from maintenance.queries import due_maintenance_plans
from organizations.models import Organization


pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username="pending-technician")


@pytest.fixture
def equipment(user):
    return Equipment.objects.create(name="Compresor", code="COMP-01", created_by=user)


def make_plan(user, equipment, **kwargs):
    defaults = {
        "organization": equipment.organization,
        "equipment": equipment,
        "created_by": user,
        "name": "Revisión",
        "strategy": "time",
        "interval_days": 30,
        "last_service_at": timezone.now() - timedelta(days=31),
    }
    defaults.update(kwargs)
    return MaintenancePlan.objects.create(**defaults)


def make_record(user, equipment, status):
    return MaintenanceRecord.objects.create(
        organization=equipment.organization, equipment=equipment,
        created_by=user, performed_by=user, performed_at=timezone.now(),
        maintenance_type="scheduled", description="Inspección", status=status,
    )


def test_time_due_boundary_and_inactive_plans(user, equipment):
    now = timezone.now()
    due = make_plan(user, equipment, last_service_at=now - timedelta(days=30))
    make_plan(user, equipment, last_service_at=now - timedelta(days=29))
    make_plan(user, equipment, active=False)
    make_plan(user, equipment, interval_days=None)

    assert list(due_maintenance_plans(equipment.organization, at=now)) == [due]


@pytest.mark.parametrize("equipment_type", ["industrial", "automotive"])
def test_meter_due_uses_latest_reading_not_highest(user, equipment, equipment_type):
    equipment.equipment_type = equipment_type
    equipment.save()
    now = timezone.now()
    plan = make_plan(
        user, equipment, strategy="meter", interval_days=None,
        interval_value=100, last_service_meter=200,
    )
    assert not due_maintenance_plans(equipment.organization, at=now).exists()
    for value, days in [(400, -2), (299, -1), (500, 1)]:
        MeterReading.objects.create(
            equipment=equipment, organization=equipment.organization,
            value=value, recorded_by=user, recorded_at=now + timedelta(days=days),
        )
    assert not due_maintenance_plans(equipment.organization, at=now).exists()
    MeterReading.objects.create(
        equipment=equipment, organization=equipment.organization,
        value=300, recorded_by=user, recorded_at=now,
    )
    assert list(due_maintenance_plans(equipment.organization, at=now)) == [plan]
    plan.last_service_meter = None
    plan.save()
    assert not due_maintenance_plans(equipment.organization, at=now).exists()


def test_categories_and_dashboard_counts(client, user, equipment):
    pending = make_record(user, equipment, "pending")
    ongoing = make_record(user, equipment, "in_progress")
    make_record(user, equipment, "completed")
    plan = make_plan(user, equipment)
    client.force_login(user)

    response = client.get(reverse("maintenance:pending"))
    assert list(response.context["results"]) == [pending, ongoing]
    assert response.context["open_count"] == 2
    assert response.context["due_count"] == 1
    response = client.get(reverse("maintenance:pending"), {"category": "due"})
    assert list(response.context["results"]) == [plan]
    assert "Vencimiento:" in response.content.decode()
    response = client.get(reverse("dashboard:index"))
    assert response.context["open_maintenance_count"] == 2
    assert response.context["due_maintenance_count"] == 1


def test_equipment_scope_and_search(client, user, equipment):
    location = Location.objects.create(name="Planta norte", organization=equipment.organization)
    equipment.location = location
    equipment.serial_number = "SER-42"
    equipment.save()
    plan = make_plan(user, equipment)
    other = Equipment.objects.create(name="Camión", code="TR-01", created_by=user)
    make_plan(user, other)
    client.force_login(user)
    for query in ["COMP-01", "Compresor", "SER-42", "Planta norte"]:
        response = client.get(reverse("maintenance:pending"), {"category": "due", "q": query})
        assert list(response.context["results"]) == [plan]
    response = client.get(reverse("maintenance:equipment-pending", args=[equipment.pk]), {"category": "due"})
    assert list(response.context["results"]) == [plan]
    assert response.context["equipment"] == equipment


def test_open_search_by_work_order_and_client_rut(client, user, equipment):
    record = make_record(user, equipment, "pending")
    record.work_order = WorkOrder.objects.create(
        number="OT-0099", client_rut="12345678-5", equipment=equipment,
        organization=equipment.organization, created_by=user,
    )
    record.save()
    make_record(user, equipment, "in_progress")
    client.force_login(user)
    for query in ["OT-0099", "12345678-5"]:
        response = client.get(reverse("maintenance:pending"), {"q": query})
        assert list(response.context["results"]) == [record]


@pytest.mark.parametrize("equipment_type,label", [("industrial", "Horómetro"), ("automotive", "Kilometraje")])
def test_due_meter_display(client, user, equipment, equipment_type, label):
    equipment.equipment_type = equipment_type
    equipment.save()
    make_plan(
        user, equipment, strategy="meter", interval_days=None,
        interval_value=100, last_service_meter=200,
    )
    MeterReading.objects.create(
        equipment=equipment, organization=equipment.organization,
        value=300, recorded_by=user,
    )
    client.force_login(user)
    response = client.get(reverse("maintenance:pending"), {"category": "due"})
    assert response.status_code == 200
    assert f"{label}:" in response.content.decode()
    assert len(response.context["results"]) == 1


def test_organization_isolation(client, user, equipment, default_region, default_comuna):
    organization = Organization.objects.create(
        name="Otra empresa", region=default_region, comuna=default_comuna,
    )
    other = Equipment.objects.create(
        name="Equipo privado", code="PRIVATE", created_by=user, organization=organization,
    )
    make_record(user, other, "pending")
    make_plan(user, other)
    client.force_login(user)
    for category in ["open", "due"]:
        response = client.get(reverse("maintenance:pending"), {"category": category})
        assert not list(response.context["results"])
        assert response.context["open_count"] == response.context["due_count"] == 0
    assert client.get(reverse("maintenance:equipment-pending", args=[other.pk])).status_code == 404
    response = client.get(reverse("dashboard:index"))
    assert response.context["open_maintenance_count"] == response.context["due_maintenance_count"] == 0


def test_pagination_preserves_search_and_category(client, user, equipment):
    for index in range(21):
        make_plan(user, equipment, name=f"Plan {index:02d}")
    client.force_login(user)
    response = client.get(reverse("maintenance:pending"), {"category": "due", "q": "COMP-01"})
    assert len(response.context["results"]) == 20
    assert response.context["due_count"] == 21
    assert "category=due&amp;q=COMP-01&amp;page=2" in response.content.decode()
    response = client.get(reverse("maintenance:pending"), {"category": "due", "q": "COMP-01", "page": 2})
    assert len(response.context["results"]) == 1


def test_anonymous_requests_require_login(client, equipment):
    for url in [reverse("maintenance:pending"), reverse("maintenance:equipment-pending", args=[equipment.pk])]:
        assert client.get(url).status_code == 302
