import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from equipment.models import Equipment, EquipmentIdentifier, Location
from organizations.models import Customer, Organization


pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username="search-user", password="test1234")


@pytest.fixture
def equipment(user):
    organization = user.organization_membership.organization
    customer = Customer.objects.create(
        organization=organization, rut="12.345.678-5", name="Transportes del Sur", customer_type="company",
    )
    location = Location.objects.create(organization=organization, name="Base central")
    equipment = Equipment.objects.create(
        organization=organization, customer=customer, name="Camión Volvo", code="TRK-001",
        serial_number="SER-100", brand="Volvo", model="FH", application="Transporte", location=location,
        created_by=user,
    )
    EquipmentIdentifier.objects.create(
        organization=organization, equipment=equipment, identifier_type="license_plate", value="ABCD12",
    )
    EquipmentIdentifier.objects.create(
        organization=organization, equipment=equipment, identifier_type="vin", value="VIN123456789",
    )
    return equipment


@pytest.mark.parametrize("query", ["12.345.678-5", "123456785", "Transportes", "Camión", "TRK-001", "SER-100", "Volvo", "FH", "Transporte", "Base central", "ABCD12", "VIN123456789"])
def test_universal_search_finds_customer_equipment_and_identifiers(client, user, equipment, query):
    client.force_login(user)

    response = client.get(reverse("dashboard:search"), {"q": query})

    assert response.status_code == 200
    assert list(response.context["equipments"]) == [equipment]


def test_universal_search_rut_lists_customer_and_all_its_equipment(client, user, equipment):
    second_equipment = Equipment.objects.create(
        organization=equipment.organization, customer=equipment.customer, name="Remolque", code="REM-001", created_by=user,
    )
    client.force_login(user)

    response = client.get(reverse("dashboard:search"), {"q": "123456785"})

    assert list(response.context["customers"]) == [equipment.customer]
    assert list(response.context["equipments"]) == [equipment, second_equipment]
    assert "Ver equipo" in response.content.decode()


def test_universal_search_is_case_insensitive(client, user, equipment):
    client.force_login(user)

    response = client.get(reverse("dashboard:search"), {"q": "abcd12"})

    assert list(response.context["equipments"]) == [equipment]


def test_universal_search_is_isolated_by_organization(client, user, equipment, default_region, default_comuna):
    other_organization = Organization.objects.create(name="Empresa ajena", region=default_region, comuna=default_comuna)
    other_customer = Customer.objects.create(
        organization=other_organization, rut="76.123.456-0", name="Cliente ajeno", customer_type="person",
    )
    Equipment.objects.create(
        organization=other_organization, customer=other_customer, name="Equipo ajeno", code="PRIVATE", created_by=user,
    )
    client.force_login(user)

    response = client.get(reverse("dashboard:search"), {"q": "PRIVATE"})

    assert not list(response.context["equipments"])
    assert not list(response.context["customers"])


def test_universal_search_requires_login(client):
    response = client.get(reverse("dashboard:search"), {"q": "algo"})

    assert response.status_code == 302
