import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from equipment.models import Equipment
from maintenance.admin import MaintenanceRecordAdmin
from maintenance.models import MaintenanceRecord


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin", password="test1234", email="admin@test.com"
    )


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.fixture
def equipment(admin_user):
    return Equipment.objects.create(
        name="Compresor principal",
        code="COMP-001",
        created_by=admin_user,
    )


@pytest.fixture
def maintenance_record(admin_user, equipment):
    return MaintenanceRecord.objects.create(
        equipment=equipment,
        maintenance_type=MaintenanceRecord.MaintenanceType.SCHEDULED,
        description="Cambio de aceite",
        performed_by=admin_user,
        performed_at=timezone.now(),
        created_by=admin_user,
    )


@pytest.mark.django_db
def test_admin_has_list_display():
    assert hasattr(MaintenanceRecordAdmin, "list_display")
    assert "equipment" in MaintenanceRecordAdmin.list_display
    assert "maintenance_type" in MaintenanceRecordAdmin.list_display
    assert "status" in MaintenanceRecordAdmin.list_display


@pytest.mark.django_db
def test_admin_has_list_filter():
    assert hasattr(MaintenanceRecordAdmin, "list_filter")
    assert "status" in MaintenanceRecordAdmin.list_filter
    assert "maintenance_type" in MaintenanceRecordAdmin.list_filter


@pytest.mark.django_db
def test_admin_has_search_fields():
    assert hasattr(MaintenanceRecordAdmin, "search_fields")
    assert "description" in MaintenanceRecordAdmin.search_fields
    assert "equipment__name" in MaintenanceRecordAdmin.search_fields


@pytest.mark.django_db
def test_admin_has_readonly_fields():
    assert hasattr(MaintenanceRecordAdmin, "readonly_fields")
    assert "created_by" in MaintenanceRecordAdmin.readonly_fields
    assert "created_at" in MaintenanceRecordAdmin.readonly_fields
    assert "updated_by" in MaintenanceRecordAdmin.readonly_fields
    assert "updated_at" in MaintenanceRecordAdmin.readonly_fields


@pytest.mark.django_db
def test_admin_has_delete_permission_returns_false(admin_user):
    from django.contrib import admin as django_admin
    model_admin = MaintenanceRecordAdmin(MaintenanceRecord, django_admin.site)
    assert model_admin.has_delete_permission(admin_user) is False
    assert model_admin.has_delete_permission(admin_user, None) is False
