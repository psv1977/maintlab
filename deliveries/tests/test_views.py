import pytest
from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse
from django.utils import timezone

from deliveries.models import Delivery
from equipment.models import Equipment


@pytest.fixture
def technician():
    user = User.objects.create_user(username="tecnico", password="test1234")
    group, _ = Group.objects.get_or_create(name="tecnicos")
    permissions = Permission.objects.filter(
        content_type__app_label="deliveries",
        content_type__model="delivery",
        codename__in=["add_delivery", "view_delivery", "change_delivery"],
    )
    group.permissions.add(*permissions)
    user.groups.add(group)
    return user


@pytest.fixture
def equipment(technician):
    return Equipment.objects.create(name="Bomba", code="BOM-001", created_by=technician)


@pytest.mark.django_db
def test_technician_creates_delivery(client, technician, equipment):
    client.force_login(technician)
    response = client.post(
        reverse("deliveries:create"),
        {
            "equipment": equipment.pk,
            "client_name": "Cliente SpA",
            "client_rut": "76.123.456-0",
            "delivered_by": technician.pk,
            "received_by": "Ana Pérez",
            "delivered_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "status": "delivered",
        },
    )

    assert response.status_code == 302
    delivery = Delivery.objects.get()
    assert delivery.client_rut == "76.123.456-0"
    assert delivery.created_by == technician


@pytest.mark.django_db
def test_delivery_requires_valid_rut(client, technician, equipment):
    client.force_login(technician)
    response = client.post(
        reverse("deliveries:create"),
        {
            "equipment": equipment.pk,
            "client_name": "Cliente SpA",
            "client_rut": "76.123.456-1",
            "delivered_by": technician.pk,
            "received_by": "Ana Pérez",
            "delivered_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "status": "delivered",
        },
    )

    assert response.status_code == 200
    assert not Delivery.objects.exists()
