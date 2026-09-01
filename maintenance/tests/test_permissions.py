import pytest
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

from maintenance.models import MaintenanceRecord


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.fixture
def tecnicos_group():
    ct = ContentType.objects.get_for_model(MaintenanceRecord)
    perms = Permission.objects.filter(
        content_type=ct,
        codename__in=["add_maintenance", "view_maintenance", "change_maintenance"],
    )
    group, _ = Group.objects.get_or_create(name="tecnicos")
    group.permissions.set(perms)
    return group


@pytest.mark.django_db
def test_maintenance_permissions_exist():
    ct = ContentType.objects.get_for_model(MaintenanceRecord)
    assert Permission.objects.filter(
        content_type=ct,
        codename="add_maintenance",
    ).exists()
    assert Permission.objects.filter(
        content_type=ct,
        codename="view_maintenance",
    ).exists()
    assert Permission.objects.filter(
        content_type=ct,
        codename="change_maintenance",
    ).exists()


@pytest.mark.django_db
def test_tecnicos_group_has_maintenance_permissions(tecnicos_group):
    ct = ContentType.objects.get_for_model(MaintenanceRecord)
    add_perm = Permission.objects.get(content_type=ct, codename="add_maintenance")
    view_perm = Permission.objects.get(content_type=ct, codename="view_maintenance")
    change_perm = Permission.objects.get(content_type=ct, codename="change_maintenance")

    assert tecnicos_group.permissions.filter(pk=add_perm.pk).exists()
    assert tecnicos_group.permissions.filter(pk=view_perm.pk).exists()
    assert tecnicos_group.permissions.filter(pk=change_perm.pk).exists()


@pytest.mark.django_db
def test_user_inherits_group_permissions(user, tecnicos_group):
    user.groups.add(tecnicos_group)

    assert user.has_perm("maintenance.add_maintenance")
    assert user.has_perm("maintenance.view_maintenance")
    assert user.has_perm("maintenance.change_maintenance")


@pytest.mark.django_db
def test_superuser_has_maintenance_permissions():
    admin = User.objects.create_superuser(username="admin", password="test1234")
    assert admin.has_perm("maintenance.add_maintenance")
    assert admin.has_perm("maintenance.view_maintenance")
    assert admin.has_perm("maintenance.change_maintenance")
