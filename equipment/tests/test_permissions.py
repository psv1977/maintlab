import pytest
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

from equipment.models import Equipment


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.fixture
def user_with_retire_perm():
    u = User.objects.create_user(username="admin_perm", password="test1234")
    perm = Permission.objects.get(codename="retire_equipment")
    u.user_permissions.add(perm)
    return u


@pytest.mark.django_db
def test_retire_permission_exists():
    ct = ContentType.objects.get_for_model(Equipment)
    perm = Permission.objects.filter(
        content_type=ct, codename="retire_equipment"
    )
    assert perm.exists()


@pytest.mark.django_db
def test_user_with_perm_has_perm(user_with_retire_perm):
    assert user_with_retire_perm.has_perm("equipment.retire_equipment")


@pytest.mark.django_db
def test_user_without_perm_does_not_have_it(user):
    assert not user.has_perm("equipment.retire_equipment")


@pytest.mark.django_db
def test_super_user_has_perm_implicitly():
    admin = User.objects.create_superuser(
        username="super", password="test1234"
    )
    assert admin.has_perm("equipment.retire_equipment")
