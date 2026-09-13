import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from organizations.models import Organization, OrganizationInvitation


@pytest.mark.django_db
def test_unknown_company_rut_starts_company_registration(client):
    response = client.post(reverse("users:register"), {"rut": "76.123.456-0"})

    assert response.status_code == 302
    assert response.url == reverse("users:register-organization")
    assert client.session["registration_organization_rut"] == "76.123.456-0"


@pytest.mark.django_db
def test_first_company_user_is_staff_and_logged_in(client, default_region, default_comuna):
    client.post(reverse("users:register"), {"rut": "76.123.456-0"})
    response = client.post(
        reverse("users:register-organization"),
        {
            "name": "Empresa Uno SpA",
            "rut": "76.123.456-0",
            "business_line": "Servicios técnicos",
            "region": default_region.pk,
            "comuna": default_comuna.pk,
            "address": "Av. Principal 123",
        },
    )

    assert response.status_code == 302
    response = client.post(
        reverse("users:register-user"),
        {
            "username": "fundador",
            "password1": "Password123!",
            "password2": "Password123!",
        },
    )

    user = User.objects.get(username="fundador")
    assert response.status_code == 302
    assert response.url == reverse("dashboard:index")
    assert user.is_staff
    assert user.organization_membership.organization.rut == "76.123.456-0"
    organization = user.organization_membership.organization
    assert organization.account_status == organization.AccountStatus.DEMO
    assert organization.demo_ends_at > timezone.now()
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_existing_company_requires_available_invitation(client, default_region, default_comuna):
    organization = Organization.objects.create(
        name="Empresa Dos", rut="11.111.111-1", region=default_region, comuna=default_comuna
    )
    administrator = User.objects.create_user(username="admin", password="test1234", is_staff=True)
    administrator.organization_membership.organization = organization
    administrator.organization_membership.save()
    invitation = OrganizationInvitation.objects.create(
        organization=organization, created_by=administrator
    )

    client.post(reverse("users:register"), {"rut": organization.rut})
    invalid_response = client.post(
        reverse("users:register-user"),
        {
            "username": "invitado",
            "password1": "Password123!",
            "password2": "Password123!",
            "invitation_code": "incorrecto",
        },
    )
    response = client.post(
        reverse("users:register-user"),
        {
            "username": "invitado",
            "password1": "Password123!",
            "password2": "Password123!",
            "invitation_code": invitation.code,
        },
    )

    invitation.refresh_from_db()
    user = User.objects.get(username="invitado")
    assert invalid_response.status_code == 200
    assert not invalid_response.context["form"].is_valid()
    assert response.status_code == 302
    assert not user.is_staff
    assert user.organization_membership.organization == organization
    assert invitation.used_by == user
    assert invitation.used_at is not None


@pytest.mark.django_db
def test_staff_can_generate_and_revoke_its_organization_invitation(client, default_region, default_comuna):
    organization = Organization.objects.create(
        name="Empresa Tres", rut="12.345.678-5", region=default_region, comuna=default_comuna
    )
    administrator = User.objects.create_user(username="admin", password="test1234", is_staff=True)
    administrator.organization_membership.organization = organization
    administrator.organization_membership.save()
    client.force_login(administrator)

    response = client.post(reverse("users:invitation-create"))
    invitation = OrganizationInvitation.objects.get()
    revoke_response = client.post(reverse("users:invitation-revoke", args=[invitation.pk]))

    invitation.refresh_from_db()
    assert response.status_code == 302
    assert invitation.organization == organization
    assert revoke_response.status_code == 302
    assert invitation.revoked_at is not None
