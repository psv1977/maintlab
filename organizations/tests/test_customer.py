import pytest
from django.contrib.auth.models import User

from organizations.forms import CustomerForm
from organizations.models import Customer


pytestmark = pytest.mark.django_db


def test_customer_form_normalizes_rut_and_scopes_uniqueness():
    user = User.objects.create_user(username="customer-user")
    organization = user.organization_membership.organization
    form = CustomerForm(
        data={"rut": "12345678-5", "name": "Ana Pérez", "customer_type": "person"}, organization=organization,
    )

    assert form.is_valid()
    customer = form.save(commit=False)
    customer.organization = organization
    customer.save()
    assert customer.rut == "12.345.678-5"

    duplicate = CustomerForm(
        data={"rut": "12.345.678-5", "name": "Duplicado", "customer_type": "person"}, organization=organization,
    )
    assert not duplicate.is_valid()
    assert "rut" in duplicate.errors
