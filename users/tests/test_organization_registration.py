import pytest
from organizations.models import Comuna, Organization, Region
from users.forms import OrganizationRegistrationForm


@pytest.fixture
def region_valparaiso():
    return Region.objects.get(name="Región de Valparaíso")


@pytest.fixture
def comuna_puerto_varas():
    return Comuna.objects.get(name="Puerto Varas")


@pytest.fixture
def comuna_valparaiso():
    return Comuna.objects.get(name="Valparaíso")


@pytest.mark.django_db
def test_organization_registration_form_valid(region_valparaiso, comuna_valparaiso):
    data = {
        "name": "Empresa Test",
        "rut": "12.345.678-5",
        "business_line": "Servicios",
        "region": region_valparaiso.pk,
        "comuna": comuna_valparaiso.pk,
        "address": "Av. Valparaíso 123",
    }
    form = OrganizationRegistrationForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_organization_registration_form_region_comuna_mismatch(
    region_valparaiso, comuna_puerto_varas
):
    data = {
        "name": "Empresa Test",
        "rut": "12345678-9",
        "business_line": "Servicios",
        "region": region_valparaiso.pk,
        "comuna": comuna_puerto_varas.pk,
        "address": "Av. Valparaíso 123",
    }
    form = OrganizationRegistrationForm(data=data)
    assert not form.is_valid()
    assert "comuna" in form.errors


@pytest.mark.django_db
def test_organization_registration_form_required_fields():
    form = OrganizationRegistrationForm(data={})
    assert not form.is_valid()
    assert "name" in form.errors
    assert "region" in form.errors
    assert "comuna" in form.errors


@pytest.mark.django_db
def test_organization_registration_form_optional_fields(region_valparaiso, comuna_valparaiso):
    data = {
        "name": "Empresa Test",
        "rut": "",
        "business_line": "",
        "region": region_valparaiso.pk,
        "comuna": comuna_valparaiso.pk,
        "address": "",
    }
    form = OrganizationRegistrationForm(data=data)
    assert form.is_valid()
