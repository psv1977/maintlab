import importlib

import pytest
from django.contrib.auth.models import Group, Permission, User
from django.apps import apps


@pytest.fixture
def tecnicos_group():
    return Group.objects.get(name="tecnicos")


@pytest.mark.django_db
def test_tecnicos_group_exists_with_exact_permissions(tecnicos_group):
    assert set(tecnicos_group.permissions.values_list("codename", flat=True)) == {
        "add_equipment",
        "view_equipment",
        "change_equipment",
    }


@pytest.mark.django_db
def test_tecnicos_member_has_operational_permissions_only(tecnicos_group):
    user = User.objects.create_user(username="tecnico", password="test1234")
    user.groups.add(tecnicos_group)

    assert user.has_perm("equipment.add_equipment")
    assert user.has_perm("equipment.view_equipment")
    assert user.has_perm("equipment.change_equipment")
    assert not user.has_perm("equipment.delete_equipment")
    assert not user.has_perm("equipment.retire_equipment")


@pytest.mark.django_db
def test_tecnicos_migration_is_idempotent(tecnicos_group):
    migration = importlib.import_module(
        "equipment.migrations.0003_create_tecnicos_group"
    )
    extra_permission = Permission.objects.get(codename="delete_equipment")
    tecnicos_group.permissions.add(extra_permission)

    migration.create_tecnicos_group(apps, None)

    tecnicos_group.refresh_from_db()
    assert set(tecnicos_group.permissions.values_list("codename", flat=True)) == {
        "add_equipment",
        "view_equipment",
        "change_equipment",
    }
