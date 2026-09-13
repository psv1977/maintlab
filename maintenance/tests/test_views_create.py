import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from equipment.models import Equipment
from maintenance.models import MaintenancePlan, MaintenanceRecord


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
    assert 'href="/equipment/new/"' in response.content.decode()


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


@pytest.mark.django_db
def test_create_view_ignores_submitted_responsible_user(client, user, equipment):
    other_user = User.objects.create_user(username="otro", password="test1234")
    client.force_login(user)
    data = {
        "equipment": equipment.pk,
        "client_rut": "11.111.111-1",
        "maintenance_type": "scheduled",
        "description": "Cambio de filtro",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
        "performed_by": other_user.pk,
    }

    response = client.post(reverse("maintenance:create"), data)

    assert response.status_code == 302
    assert MaintenanceRecord.objects.get(description="Cambio de filtro").performed_by == user


@pytest.mark.django_db
def test_create_view_resets_only_selected_plan(client, user, equipment):
    time_plan = MaintenancePlan.objects.create(
        equipment=equipment,
        name="Inspección semestral",
        strategy=MaintenancePlan.Strategy.TIME,
        interval_days=180,
        created_by=user,
    )
    meter_plan = MaintenancePlan.objects.create(
        equipment=equipment,
        name="Servicio por uso",
        strategy=MaintenancePlan.Strategy.METER,
        interval_value="500.00",
        created_by=user,
        last_service_meter="1000.00",
    )
    client.force_login(user)
    performed_at = timezone.now().replace(microsecond=0)
    response = client.post(
        reverse("maintenance:create"),
        {
            "equipment": equipment.pk,
            "client_rut": "11.111.111-1",
            "maintenance_type": "scheduled",
            "description": "Inspección semestral",
            "performed_at": performed_at.strftime("%Y-%m-%dT%H:%M"),
            "status": "pending",
            "reset_plans": [time_plan.pk],
            "meter_reading": "1200.00",
        },
    )

    assert response.status_code == 302
    time_plan.refresh_from_db()
    meter_plan.refresh_from_db()
    assert time_plan.last_service_at is not None
    assert time_plan.last_service_meter is None
    assert meter_plan.last_service_meter == 1000
