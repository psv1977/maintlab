import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from equipment.models import Equipment


@pytest.fixture
def staff_user():
    return User.objects.create_user(
        username="staff", password="test1234", is_staff=True
    )


@pytest.fixture
def staff_user_with_view(staff_user):
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    ct = ContentType.objects.get_for_model(Equipment)
    perm = Permission.objects.get(content_type=ct, codename="view_equipment")
    staff_user.user_permissions.add(perm)
    return staff_user


@pytest.fixture
def staff_user_with_change(staff_user):
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    ct = ContentType.objects.get_for_model(Equipment)
    perm = Permission.objects.get(content_type=ct, codename="change_equipment")
    staff_user.user_permissions.add(perm)
    return staff_user


@pytest.fixture
def superuser():
    return User.objects.create_superuser(username="super", password="test1234")


@pytest.fixture
def equipment(staff_user):
    return Equipment.objects.create(
        name="Compresor principal",
        code="COMP-001",
        created_by=staff_user,
    )


CHANGELIST = "admin:equipment_equipment_changelist"
CHANGE = "admin:equipment_equipment_change"
DELETE = "admin:equipment_equipment_delete"


@pytest.mark.django_db
def test_staff_without_permissions_cannot_see_equipment(client, staff_user):
    client.force_login(staff_user)

    response = client.get(reverse(CHANGELIST))

    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_with_view_can_see_changelist(client, staff_user_with_view):
    client.force_login(staff_user_with_view)

    response = client.get(reverse(CHANGELIST))

    assert response.status_code == 200


@pytest.mark.django_db
def test_staff_with_change_can_edit(client, staff_user_with_change, equipment):
    client.force_login(staff_user_with_change)

    response = client.get(reverse(CHANGE, args=[equipment.pk]))

    assert response.status_code == 200


@pytest.mark.django_db
def test_superuser_has_full_access(client, superuser, equipment):
    client.force_login(superuser)

    changelist = client.get(reverse(CHANGELIST))
    change = client.get(reverse(CHANGE, args=[equipment.pk]))

    assert changelist.status_code == 200
    assert change.status_code == 200


@pytest.mark.django_db
def test_has_delete_permission_is_false(client, superuser, equipment):
    client.force_login(superuser)

    response = client.get(reverse(CHANGE, args=[equipment.pk]))

    assert response.status_code == 200
    assert b"Delete" not in response.content
    assert b"Eliminar" not in response.content


@pytest.mark.django_db
def test_cannot_delete_individual_via_admin(client, superuser, equipment):
    client.force_login(superuser)

    response = client.post(
        reverse(DELETE, args=[equipment.pk]),
        {"post": "yes"},
    )

    assert response.status_code == 403
    assert Equipment.objects.filter(pk=equipment.pk).exists()


@pytest.mark.django_db
def test_cannot_delete_mass_via_admin(client, superuser, equipment):
    client.force_login(superuser)

    response = client.post(
        reverse(CHANGELIST),
        {
            "action": "delete_selected",
            "_selected_action": [str(equipment.pk)],
            "post": "yes",
        },
    )

    assert Equipment.objects.filter(pk=equipment.pk).exists()


@pytest.mark.django_db
def test_audit_fields_visible(client, superuser, equipment):
    client.force_login(superuser)

    response = client.get(reverse(CHANGE, args=[equipment.pk]))

    assert response.status_code == 200
    assert b"created_by" in response.content
    assert b"created_at" in response.content
