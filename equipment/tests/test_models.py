import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from equipment.models import Equipment


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.mark.django_db
def test_creation(user):
    eq = Equipment.objects.create(
        name="Compresor A", code="COMP-001", created_by=user
    )
    assert eq.pk is not None
    assert eq.name == "Compresor A"
    assert eq.code == "COMP-001"


@pytest.mark.django_db
def test_status_default_operational(user):
    eq = Equipment.objects.create(name="Equipo X", code="EQ-001", created_by=user)
    assert eq.status == Equipment.Status.OPERATIONAL


@pytest.mark.django_db
def test_updated_by_and_updated_at_are_null_initially(user):
    eq = Equipment.objects.create(name="Equipo Y", code="EQ-002", created_by=user)
    assert eq.updated_by is None
    assert eq.updated_at is None


@pytest.mark.django_db
def test_created_at_is_automatic(user):
    eq = Equipment.objects.create(name="Equipo Z", code="EQ-003", created_by=user)
    assert eq.created_at is not None


@pytest.mark.django_db
def test_name_max_length_rejected(user):
    eq = Equipment(name="X" * 201, code="EQ-004", created_by=user)
    with pytest.raises(ValidationError) as exc_info:
        eq.full_clean()
    assert "name" in exc_info.value.message_dict


@pytest.mark.django_db
def test_code_max_length_rejected(user):
    eq = Equipment(name="Equipo W", code="X" * 51, created_by=user)
    with pytest.raises(ValidationError) as exc_info:
        eq.full_clean()
    assert "code" in exc_info.value.message_dict


@pytest.mark.django_db
def test_invalid_status_rejected(user):
    eq = Equipment(
        name="Equipo V", code="EQ-005", status="invalid", created_by=user
    )
    with pytest.raises(ValidationError) as exc_info:
        eq.full_clean()
    assert "status" in exc_info.value.message_dict


@pytest.mark.django_db
def test_duplicate_code_rejected(user):
    Equipment.objects.create(name="Primero", code="DUP-001", created_by=user)
    with pytest.raises(IntegrityError):
        Equipment.objects.create(name="Segundo", code="DUP-001", created_by=user)


@pytest.mark.django_db
def test_str_returns_name(user):
    eq = Equipment(name="Bomba Hidráulica", code="BH-001", created_by=user)
    assert str(eq) == "Bomba Hidráulica"


@pytest.mark.django_db
def test_ordering_is_by_name(user):
    Equipment.objects.create(name="Zeta", code="ORD-002", created_by=user)
    Equipment.objects.create(name="Alfa", code="ORD-001", created_by=user)
    Equipment.objects.create(name="Omega", code="ORD-003", created_by=user)
    names = list(Equipment.objects.values_list("name", flat=True))
    assert names == ["Alfa", "Omega", "Zeta"]


@pytest.mark.django_db
def test_description_and_serial_number_optional(user):
    eq = Equipment.objects.create(name="Equipo O", code="OPT-001", created_by=user)
    assert eq.description == ""
    assert eq.serial_number == ""


@pytest.mark.django_db
def test_status_choices_are_valid(user):
    for status, _ in Equipment.Status.choices:
        eq = Equipment(
            name=f"Eq-{status}", code=f"ST-{status}", status=status, created_by=user
        )
        eq.full_clean()
        eq.save()
