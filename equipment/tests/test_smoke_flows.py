import pytest
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from equipment.models import Equipment


@pytest.fixture
def tecnico():
    u = User.objects.create_user(username="tecnico", password="test1234")
    ct = ContentType.objects.get_for_model(Equipment)
    perms = Permission.objects.filter(
        content_type=ct,
        codename__in=["add_equipment", "view_equipment", "change_equipment"],
    )
    u.user_permissions.set(perms)
    return u


@pytest.fixture
def admin_user():
    u = User.objects.create_user(username="admin_user", password="test1234")
    ct = ContentType.objects.get_for_model(Equipment)
    perm = Permission.objects.get(content_type=ct, codename="retire_equipment")
    u.user_permissions.add(perm)
    return u


@pytest.mark.django_db
def test_flujo_completo_crear_consultar_editar_retirar(client, tecnico, admin_user):
    """Smoke: recorre los 4 flujos de spec §7 de punta a punta."""

    # --- Flujo 1: Crear equipo ---
    client.force_login(tecnico)
    data = {
        "name": "Compresor industrial",
        "code": "CIMP-001",
        "description": "Compresor de alta presión",
        "serial_number": "SN-COMP-001",
        "status": "operational",
    }
    response = client.post(reverse("equipment:create"), data)
    assert response.status_code == 302
    assert response.url == reverse("equipment:list")

    equipment = Equipment.objects.get(code="CIMP-001")
    assert equipment.name == "Compresor industrial"
    assert equipment.status == "operational"
    assert equipment.created_by == tecnico
    assert equipment.created_at is not None
    assert equipment.updated_by is None
    assert equipment.updated_at is None

    # --- Flujo 2: Consultar listado y buscar ---
    response = client.get(reverse("equipment:list"))
    assert response.status_code == 200
    assert equipment in response.context["equipments"]

    response = client.get(reverse("equipment:list"), {"q": "CIMP-001"})
    assert response.status_code == 200
    assert equipment in response.context["equipments"]

    response = client.get(reverse("equipment:list"), {"q": "compresor"})
    assert response.status_code == 200
    assert equipment in response.context["equipments"]

    response = client.get(reverse("equipment:list"), {"status": "operational"})
    assert response.status_code == 200
    assert equipment in response.context["equipments"]

    # --- Flujo 3: Editar equipo ---
    edit_data = {
        "name": "Compresor industrial v2",
        "code": "CIMP-001",
        "description": "Actualizado",
        "serial_number": "SN-COMP-001",
        "status": "in_maintenance",
    }
    response = client.post(reverse("equipment:update", args=[equipment.pk]), edit_data)
    assert response.status_code == 302
    assert response.url == reverse("equipment:detail", args=[equipment.pk])

    equipment.refresh_from_db()
    assert equipment.name == "Compresor industrial v2"
    assert equipment.description == "Actualizado"
    assert equipment.status == "in_maintenance"
    assert equipment.updated_by == tecnico
    assert equipment.updated_at is not None

    # --- Flujo 4: Retirar equipo ---
    client.force_login(admin_user)
    response = client.get(reverse("equipment:retire", args=[equipment.pk]))
    assert response.status_code == 200
    assert b"Confirmar retiro" in response.content

    response = client.post(reverse("equipment:retire", args=[equipment.pk]))
    assert response.status_code == 302
    assert response.url == reverse("equipment:detail", args=[equipment.pk])

    equipment.refresh_from_db()
    assert equipment.status == "retired"
    assert equipment.name == "Compresor industrial v2"
    assert equipment.code == "CIMP-001"
    assert equipment.created_by == tecnico
    assert equipment.created_at is not None

    # --- Verificar que el retirado sigue consultable ---
    response = client.get(reverse("equipment:list"))
    assert response.status_code == 200
    assert equipment in response.context["equipments"]

    response = client.get(reverse("equipment:detail", args=[equipment.pk]))
    assert response.status_code == 200
    assert b"Retirado" in response.content

    response = client.get(reverse("equipment:list"), {"q": "compresor"})
    assert response.status_code == 200
    assert equipment in response.context["equipments"]

    # --- Verificar que nunca se puede eliminar ---
    response = client.post(reverse("admin:equipment_equipment_delete", args=[equipment.pk]), {"post": "yes"})
    assert Equipment.objects.filter(pk=equipment.pk).exists()
