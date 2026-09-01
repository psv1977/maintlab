import pytest
from django.contrib.auth.models import User
from django.db.models.deletion import ProtectedError
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
def test_cannot_delete_maintenance_record(maintenance_record):
    with pytest.raises(ProtectedError):
        maintenance_record.delete()


@pytest.mark.django_db
def test_cannot_bulk_delete_maintenance_records(maintenance_record):
    with pytest.raises(ProtectedError):
        MaintenanceRecord.objects.filter(pk=maintenance_record.pk).delete()
