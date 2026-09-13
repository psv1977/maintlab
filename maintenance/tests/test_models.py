import pytest
from django.contrib.auth.models import User
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
def test_create_maintenance_record(maintenance_record):
    assert maintenance_record.pk is not None
    assert maintenance_record.equipment.code == "COMP-001"
    assert maintenance_record.maintenance_type == "scheduled"
    assert maintenance_record.description == "Cambio de aceite"
    assert maintenance_record.status == "pending"
    assert maintenance_record.notes == ""


@pytest.mark.django_db
def test_maintenance_record_str(maintenance_record):
    assert str(maintenance_record) == "Compresor principal - Programado"


@pytest.mark.django_db
def test_maintenance_record_default_status(maintenance_record):
    assert maintenance_record.status == MaintenanceRecord.Status.PENDING


@pytest.mark.django_db
def test_maintenance_record_ordering(user, equipment):
    record1 = MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type=MaintenanceRecord.MaintenanceType.SCHEDULED,
        description="Mantenimiento 1",
        performed_by=user,
        performed_at=timezone.now() - timezone.timedelta(days=1),
        created_by=user,
    )
    record2 = MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type=MaintenanceRecord.MaintenanceType.UNSCHEDULED,
        description="Mantenimiento 2",
        performed_by=user,
        performed_at=timezone.now(),
        created_by=user,
    )

    records = list(MaintenanceRecord.objects.all())
    assert records[0] == record2
    assert records[1] == record1


@pytest.mark.django_db
def test_maintenance_record_optional_fields(user, equipment):
    record = MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type=MaintenanceRecord.MaintenanceType.UNSCHEDULED,
        description="Reparación urgente",
        performed_by=user,
        performed_at=timezone.now(),
        next_maintenance=None,
        notes="",
        created_by=user,
    )
    assert record.next_maintenance is None
    assert record.notes == ""


@pytest.mark.django_db
def test_maintenance_record_with_optional_fields(user, equipment):
    next_date = timezone.now() + timezone.timedelta(days=30)
    record = MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type=MaintenanceRecord.MaintenanceType.SCHEDULED,
        description="Revisión programada",
        performed_by=user,
        performed_at=timezone.now(),
        next_maintenance=next_date,
        notes="Próximo cambio de filtro",
        created_by=user,
    )
    assert record.next_maintenance == next_date
    assert record.notes == "Próximo cambio de filtro"


@pytest.mark.django_db
def test_maintenance_type_choices():
    assert MaintenanceRecord.MaintenanceType.SCHEDULED == "scheduled"
    assert MaintenanceRecord.MaintenanceType.UNSCHEDULED == "unscheduled"


@pytest.mark.django_db
def test_status_choices():
    assert MaintenanceRecord.Status.PENDING == "pending"
    assert MaintenanceRecord.Status.IN_PROGRESS == "in_progress"
    assert MaintenanceRecord.Status.COMPLETED == "completed"


@pytest.mark.django_db
def test_maintenance_record_audit_fields(maintenance_record, user):
    assert maintenance_record.created_by == user
    assert maintenance_record.created_at is not None
    assert maintenance_record.updated_by is None
    assert maintenance_record.updated_at is None


@pytest.mark.django_db
def test_maintenance_record_meta_ordering():
    assert MaintenanceRecord._meta.ordering == ["-performed_at"]


@pytest.mark.django_db
def test_maintenance_record_meta_verbose_name():
    assert MaintenanceRecord._meta.verbose_name == "registro de mantenimiento"
    assert MaintenanceRecord._meta.verbose_name_plural == "registros de mantenimiento"


@pytest.mark.django_db
def test_maintenance_record_equipment_relationship(maintenance_record, equipment):
    assert maintenance_record.equipment == equipment
    assert maintenance_record in equipment.maintenance_records.all()


@pytest.mark.django_db
def test_time_plan_is_due_after_interval(user, equipment):
    plan = MaintenancePlan.objects.create(
        equipment=equipment,
        name="Inspección semestral",
        strategy=MaintenancePlan.Strategy.TIME,
        interval_days=180,
        created_by=user,
        last_service_at=timezone.now() - timezone.timedelta(days=181),
    )

    assert plan.is_due()


@pytest.mark.django_db
def test_meter_plan_is_due_after_interval(user, equipment):
    plan = MaintenancePlan.objects.create(
        equipment=equipment,
        name="Servicio por uso",
        strategy=MaintenancePlan.Strategy.METER,
        interval_value="500.00",
        created_by=user,
        last_service_meter="1000.00",
    )

    assert not plan.is_due(meter_value=1499)
    assert plan.is_due(meter_value=1500)
