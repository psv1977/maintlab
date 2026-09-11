import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from deliveries.forms import DeliveryForm
from equipment.models import Equipment
from maintenance.models import WorkOrder


@pytest.mark.django_db
def test_delivery_form_normalizes_client_rut():
    user = User.objects.create_user(username="tecnico")
    equipment = Equipment.objects.create(name="Bomba", code="BOM-001", created_by=user)
    form = DeliveryForm(
        data={
            "equipment": equipment.pk,
            "client_name": "Cliente SpA",
            "client_rut": "761234560",
            "delivered_by": user.pk,
            "received_by": "Ana Pérez",
            "delivered_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "status": "delivered",
        }
    )

    assert form.is_valid()
    assert form.cleaned_data["client_rut"] == "76.123.456-0"


@pytest.mark.django_db
def test_delivery_form_does_not_expose_responsible_user():
    form = DeliveryForm()

    assert "delivered_by" not in form.fields


@pytest.mark.django_db
def test_delivery_form_rejects_work_order_from_another_equipment():
    user = User.objects.create_user(username="tecnico")
    equipment = Equipment.objects.create(name="Bomba", code="BOM-001", created_by=user)
    other_equipment = Equipment.objects.create(name="Motor", code="MOT-001", created_by=user)
    work_order = WorkOrder.objects.create(
        number="OT-0001", client_rut="76.123.456-0", equipment=other_equipment, created_by=user
    )
    form = DeliveryForm(
        data={
            "equipment": equipment.pk,
            "work_order": work_order.pk,
            "client_name": "Cliente SpA",
            "client_rut": "76.123.456-0",
            "delivered_by": user.pk,
            "received_by": "Ana Pérez",
            "delivered_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "status": "delivered",
        }
    )

    assert not form.is_valid()
    assert "work_order" in form.errors
