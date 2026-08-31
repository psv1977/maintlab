import pytest
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models.deletion import ProtectedError

from equipment.models import Equipment


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.mark.django_db
def test_instance_delete_is_blocked_and_object_persists(user):
    equipment = Equipment.objects.create(
        name="Compresor", code="COMP-001", created_by=user
    )

    with pytest.raises(ProtectedError):
        with transaction.atomic():
            equipment.delete()

    assert Equipment.objects.filter(pk=equipment.pk).exists()


@pytest.mark.django_db
def test_queryset_delete_is_blocked_and_objects_persist(user):
    first = Equipment.objects.create(
        name="Compresor", code="COMP-001", created_by=user
    )
    second = Equipment.objects.create(
        name="Bomba", code="BOMB-001", created_by=user
    )

    with pytest.raises(ProtectedError):
        with transaction.atomic():
            Equipment.objects.all().delete()

    assert Equipment.objects.filter(pk__in=[first.pk, second.pk]).count() == 2
