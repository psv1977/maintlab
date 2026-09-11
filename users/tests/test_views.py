import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from equipment.models import Equipment


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin", password="test1234", email="admin@test.com"
    )


@pytest.fixture
def staff_user():
    return User.objects.create_user(
        username="staff", password="test1234", is_staff=True
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.mark.django_db
def test_user_list_requires_staff(client, regular_user):
    client.force_login(regular_user)
    response = client.get(reverse("users:list"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_list_requires_login(client):
    response = client.get(reverse("users:list"))
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_user_list_view(client, staff_user, regular_user):
    client.force_login(staff_user)
    response = client.get(reverse("users:list"))
    assert response.status_code == 200
    assert regular_user in response.context["users"]


@pytest.mark.django_db
def test_user_detail_requires_staff(client, regular_user):
    client.force_login(regular_user)
    response = client.get(reverse("users:detail", args=[regular_user.pk]))
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_detail_view(client, staff_user, regular_user):
    client.force_login(staff_user)
    response = client.get(reverse("users:detail", args=[regular_user.pk]))
    assert response.status_code == 200
    assert response.context["user_obj"] == regular_user


@pytest.mark.django_db
def test_user_create_requires_staff(client, regular_user):
    client.force_login(regular_user)
    response = client.get(reverse("users:create"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_create_view_get(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("users:create"))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_user_create_view_post_valid(client, staff_user):
    client.force_login(staff_user)
    data = {
        "username": "newuser",
        "password1": "testpass123!",
        "password2": "testpass123!",
    }
    response = client.post(reverse("users:create"), data)
    assert response.status_code == 302
    assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_staff_user_cannot_assign_staff_on_creation(client, staff_user):
    client.force_login(staff_user)
    data = {
        "username": "newuser",
        "password1": "testpass123!",
        "password2": "testpass123!",
        "is_staff": True,
    }

    response = client.post(reverse("users:create"), data)

    assert response.status_code == 302
    assert not User.objects.get(username="newuser").is_staff


@pytest.mark.django_db
def test_user_update_requires_staff(client, regular_user):
    client.force_login(regular_user)
    response = client.get(reverse("users:update", args=[regular_user.pk]))
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_update_view_post_valid(client, staff_user, regular_user):
    client.force_login(staff_user)
    data = {
        "username": regular_user.username,
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan@test.com",
        "is_active": True,
        "is_staff": False,
    }
    response = client.post(reverse("users:update", args=[regular_user.pk]), data)
    assert response.status_code == 302
    regular_user.refresh_from_db()
    assert regular_user.first_name == "Juan"
    assert regular_user.last_name == "Pérez"


@pytest.mark.django_db
def test_staff_can_confirm_deactivation_of_regular_user(client, staff_user, regular_user):
    client.force_login(staff_user)

    confirmation = client.get(reverse("users:deactivate", args=[regular_user.pk]))
    assert confirmation.status_code == 200
    assert b"Confirmar desactivaci" in confirmation.content

    not_confirmed = client.post(reverse("users:deactivate", args=[regular_user.pk]))
    assert not_confirmed.status_code == 200
    regular_user.refresh_from_db()
    assert regular_user.is_active

    response = client.post(
        reverse("users:deactivate", args=[regular_user.pk]),
        {"confirm": "yes"},
    )
    assert response.status_code == 302
    regular_user.refresh_from_db()
    assert not regular_user.is_active
    assert not regular_user.is_staff


@pytest.mark.django_db
def test_deactivation_preserves_user_history(client, staff_user, regular_user):
    equipment = Equipment.objects.create(
        name="Equipo histórico",
        code="HIST-001",
        created_by=regular_user,
    )
    client.force_login(staff_user)

    client.post(
        reverse("users:deactivate", args=[regular_user.pk]),
        {"confirm": "yes"},
    )

    assert Equipment.objects.get(pk=equipment.pk).created_by == regular_user


@pytest.mark.django_db
def test_staff_cannot_deactivate_another_staff_user(client, staff_user):
    other_staff = User.objects.create_user(username="otro_staff", is_staff=True)
    client.force_login(staff_user)

    response = client.get(reverse("users:deactivate", args=[other_staff.pk]))

    assert response.status_code == 403


@pytest.mark.django_db
def test_superuser_can_deactivate_staff_user(client, admin_user, staff_user):
    client.force_login(admin_user)

    response = client.post(
        reverse("users:deactivate", args=[staff_user.pk]),
        {"confirm": "yes"},
    )

    assert response.status_code == 302
    staff_user.refresh_from_db()
    assert not staff_user.is_active
    assert not staff_user.is_staff


@pytest.mark.django_db
def test_user_cannot_deactivate_own_account(client, staff_user):
    client.force_login(staff_user)

    response = client.get(reverse("users:deactivate", args=[staff_user.pk]))

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_groups_requires_staff(client, regular_user):
    client.force_login(regular_user)
    response = client.get(reverse("users:groups", args=[regular_user.pk]))
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_groups_view_get(client, staff_user, regular_user):
    client.force_login(staff_user)
    response = client.get(reverse("users:groups", args=[regular_user.pk]))
    assert response.status_code == 200
    assert "form" in response.context
