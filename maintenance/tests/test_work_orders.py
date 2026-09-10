import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from equipment.models import Equipment
from maintenance.models import MaintenanceRecord, WorkOrder


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.fixture
def equipment(user):
    return Equipment.objects.create(name="Compresor", code="COMP-001", created_by=user)


@pytest.mark.django_db
def test_create_maintenance_generates_work_order(client, user, equipment):
    client.force_login(user)
    response = client.post(
        reverse("maintenance:create"),
        {
            "equipment": equipment.pk,
            "client_rut": "76.123.456-0",
            "maintenance_type": "scheduled",
            "description": "Inspección",
            "performed_by": user.pk,
            "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "status": "pending",
        },
    )

    assert response.status_code == 302
    work_order = WorkOrder.objects.get()
    record = MaintenanceRecord.objects.get()
    assert work_order.number == "OT-0001"
    assert work_order.client_rut == "76.123.456-0"
    assert record.work_order == work_order


@pytest.mark.django_db
def test_create_maintenance_registers_end_date_and_responsible(client, user, equipment):
    client.force_login(user)
    completed_at = timezone.now().replace(second=0, microsecond=0)
    client.post(
        reverse("maintenance:create"),
        {
            "equipment": equipment.pk,
            "client_rut": "11.111.111-1",
            "maintenance_type": "unscheduled",
            "description": "Reparación",
            "performed_by": user.pk,
            "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "completed_at": completed_at.strftime("%Y-%m-%dT%H:%M"),
            "status": "in_progress",
        },
    )

    record = MaintenanceRecord.objects.get()
    assert record.performed_by == user
    assert record.completed_at is not None


@pytest.mark.django_db
def test_work_order_numbers_are_correlative(client, user, equipment):
    client.force_login(user)
    data = {
        "equipment": equipment.pk,
        "client_rut": "11.111.111-1",
        "maintenance_type": "scheduled",
        "description": "Inspección",
        "performed_by": user.pk,
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
    }

    client.post(reverse("maintenance:create"), data)
    data["description"] = "Lubricación"
    client.post(reverse("maintenance:create"), data)

    assert list(WorkOrder.objects.values_list("number", flat=True)) == [
        "OT-0002",
        "OT-0001",
    ]
