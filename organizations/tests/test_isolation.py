from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from equipment.models import Equipment
from organizations.models import Organization


@pytest.mark.django_db
def test_user_cannot_see_another_organization_equipment(client, default_region, default_comuna):
    first_organization = Organization.objects.create(
        name="Empresa uno", region=default_region, comuna=default_comuna
    )
    second_organization = Organization.objects.create(
        name="Empresa dos", region=default_region, comuna=default_comuna
    )
    first_user = User.objects.create_user(username="uno", password="test1234")
    second_user = User.objects.create_user(username="dos", password="test1234")
    first_user.organization_membership.organization = first_organization
    first_user.organization_membership.save()
    second_user.organization_membership.organization = second_organization
    second_user.organization_membership.save()
    first_equipment = Equipment.objects.create(
        organization=first_organization, name="Equipo uno", code="EQ-001", created_by=first_user
    )
    second_equipment = Equipment.objects.create(
        organization=second_organization, name="Equipo dos", code="EQ-001", created_by=second_user
    )

    client.force_login(first_user)
    response = client.get(reverse("equipment:list"))

    assert response.status_code == 200
    assert list(response.context["equipments"]) == [first_equipment]
    assert client.get(reverse("equipment:detail", args=[second_equipment.pk])).status_code == 404


@pytest.mark.django_db
def test_import_is_only_available_to_staff(client):
    user = User.objects.create_user(username="tecnico", password="test1234")
    client.force_login(user)

    assert client.get(reverse("equipment:import")).status_code == 403

    user.is_staff = True
    user.save(update_fields=["is_staff"])
    assert client.get(reverse("equipment:import")).status_code == 200


@pytest.mark.django_db
def test_expired_demo_allows_reading_but_blocks_writes(client, default_region, default_comuna):
    organization = Organization.objects.create(
        name="Demo vencida",
        region=default_region,
        comuna=default_comuna,
        account_status=Organization.AccountStatus.DEMO,
        demo_ends_at=timezone.now() - timedelta(days=1),
    )
    user = User.objects.create_user(username="demo", password="test1234")
    user.organization_membership.organization = organization
    user.organization_membership.save()
    client.force_login(user)

    assert client.get(reverse("equipment:list")).status_code == 200
    response = client.post(
        reverse("equipment:create"),
        {"name": "Equipo bloqueado", "code": "BLOCK-001"},
    )

    assert response.status_code == 403
    assert not Equipment.objects.filter(code="BLOCK-001").exists()
