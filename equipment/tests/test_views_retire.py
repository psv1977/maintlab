import pytest
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from equipment.models import Equipment


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.fixture
def user_with_retire_perm():
    ct = ContentType.objects.get_for_model(Equipment)
    perm = Permission.objects.get(content_type=ct, codename="retire_equipment")
    u = User.objects.create_user(username="admin_perm", password="test1234")
    u.user_permissions.add(perm)
    return u


@pytest.fixture
def tecnicos_user():
    ct = ContentType.objects.get_for_model(Equipment)
    group, _ = Group.objects.get_or_create(name="tecnicos")
    perms = Permission.objects.filter(
        content_type=ct, codename__in=["add_equipment", "view_equipment", "change_equipment"]
    )
    group.permissions.set(perms)
    u = User.objects.create_user(username="tecnico_group", password="test1234")
    u.groups.add(group)
    return u


@pytest.fixture
def equipment(user):
    return Equipment.objects.create(
        name="Compresor principal",
        code="COMP-001",
        created_by=user,
    )


@pytest.mark.django_db
def test_user_with_perm_can_see_confirmation_get(client, user_with_retire_perm, equipment):
    client.force_login(user_with_retire_perm)

    response = client.get(reverse("equipment:retire", args=[equipment.pk]))

    assert response.status_code == 200
    assert equipment.name.encode() in response.content
    assert b"Confirmar retiro" in response.content


@pytest.mark.django_db
def test_user_with_perm_can_retire_equipment(client, user_with_retire_perm, equipment):
    client.force_login(user_with_retire_perm)

    response = client.post(reverse("equipment:retire", args=[equipment.pk]))

    assert response.status_code == 302
    assert response.url == reverse("equipment:detail", args=[equipment.pk])
    equipment.refresh_from_db()
    assert equipment.status == Equipment.Status.RETIRED


@pytest.mark.django_db
def test_retired_equipment_data_is_preserved(client, user_with_retire_perm, equipment):
    client.force_login(user_with_retire_perm)

    client.post(reverse("equipment:retire", args=[equipment.pk]))

    equipment.refresh_from_db()
    assert equipment.name == "Compresor principal"
    assert equipment.code == "COMP-001"
    assert equipment.created_by == equipment.created_by
    assert equipment.created_at is not None


@pytest.mark.django_db
def test_retired_equipment_still_in_list(client, user_with_retire_perm, equipment):
    client.force_login(user_with_retire_perm)

    client.post(reverse("equipment:retire", args=[equipment.pk]))

    response = client.get(reverse("equipment:list"))
    assert response.status_code == 200
    assert equipment in response.context["equipments"]


@pytest.mark.django_db
def test_retired_equipment_still_in_detail(client, user_with_retire_perm, equipment):
    client.force_login(user_with_retire_perm)

    client.post(reverse("equipment:retire", args=[equipment.pk]))

    response = client.get(reverse("equipment:detail", args=[equipment.pk]))
    assert response.status_code == 200
    assert b"Retirado" in response.content


@pytest.mark.django_db
def test_retired_equipment_still_in_search(client, user_with_retire_perm, equipment):
    client.force_login(user_with_retire_perm)

    client.post(reverse("equipment:retire", args=[equipment.pk]))

    response = client.get(reverse("equipment:list"), {"q": "compresor"})
    assert response.status_code == 200
    assert equipment in response.context["equipments"]


@pytest.mark.django_db
def test_tecnicos_user_gets_403_on_get(client, tecnicos_user, equipment):
    client.force_login(tecnicos_user)

    response = client.get(reverse("equipment:retire", args=[equipment.pk]))

    assert response.status_code == 403


@pytest.mark.django_db
def test_tecnicos_user_gets_403_on_post(client, tecnicos_user, equipment):
    client.force_login(tecnicos_user)

    response = client.post(reverse("equipment:retire", args=[equipment.pk]))

    assert response.status_code == 403
    equipment.refresh_from_db()
    assert equipment.status == Equipment.Status.OPERATIONAL


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_login(client, equipment):
    response = client.get(reverse("equipment:retire", args=[equipment.pk]))

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_get_does_not_mutate_status(client, user_with_retire_perm, equipment):
    client.force_login(user_with_retire_perm)

    client.get(reverse("equipment:retire", args=[equipment.pk]))

    equipment.refresh_from_db()
    assert equipment.status == Equipment.Status.OPERATIONAL


@pytest.mark.django_db
def test_superuser_can_retire_implies(client, equipment):
    superuser = User.objects.create_superuser(
        username="super", password="test1234"
    )
    client.force_login(superuser)

    response = client.post(reverse("equipment:retire", args=[equipment.pk]))

    assert response.status_code == 302
    equipment.refresh_from_db()
    assert equipment.status == Equipment.Status.RETIRED
