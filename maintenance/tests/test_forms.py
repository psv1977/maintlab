import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from equipment.models import Equipment
from maintenance.forms import MaintenanceForm
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
def retired_equipment(user):
    return Equipment.objects.create(
        name="Equipo retirado",
        code="RET-001",
        status=Equipment.Status.RETIRED,
        created_by=user,
    )


@pytest.mark.django_db
def test_maintenance_form_valid(equipment):
    data = {
        "equipment": equipment.pk,
        "client_rut": "11.111.111-1",
        "maintenance_type": "scheduled",
        "description": "Cambio de aceite",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "status": "pending",
    }
    form = MaintenanceForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_maintenance_form_does_not_expose_responsible_user():
    form = MaintenanceForm()

    assert "performed_by" not in form.fields


@pytest.mark.django_db
def test_maintenance_form_required_fields():
    form = MaintenanceForm(data={})
    assert not form.is_valid()
    assert "equipment" in form.errors
    assert "client_rut" in form.errors
    assert "maintenance_type" in form.errors
    assert "description" in form.errors
    assert "performed_at" in form.errors


@pytest.mark.django_db
def test_maintenance_form_excludes_retired_equipment(equipment, retired_equipment):
    form = MaintenanceForm()
    queryset = form.fields["equipment"].queryset
    assert equipment in queryset
    assert retired_equipment not in queryset


@pytest.mark.django_db
def test_maintenance_form_status_excludes_completed():
    form = MaintenanceForm()
    status_choices = form.fields["status"].choices
    status_values = [choice[0] for choice in status_choices]
    assert "completed" not in status_values


@pytest.mark.django_db
def test_maintenance_form_optional_fields(equipment):
    data = {
        "equipment": equipment.pk,
        "client_rut": "11.111.111-1",
        "maintenance_type": "unscheduled",
        "description": "Reparación urgente",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "next_maintenance": "",
        "status": "pending",
        "notes": "",
    }
    form = MaintenanceForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_maintenance_form_with_notes(equipment):
    data = {
        "equipment": equipment.pk,
        "client_rut": "11.111.111-1",
        "maintenance_type": "scheduled",
        "description": "Revisión programada",
        "performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "next_maintenance": (timezone.now() + timezone.timedelta(days=30)).strftime(
            "%Y-%m-%dT%H:%M"
        ),
        "status": "pending",
        "notes": "Próximo cambio de filtro",
    }
    form = MaintenanceForm(data=data)
    assert form.is_valid()
