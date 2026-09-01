import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from equipment.models import Equipment


@pytest.fixture
def user():
    return User.objects.create_user(username="tecnico", password="test1234")


@pytest.fixture
def equipments(user):
    return [
        Equipment.objects.create(
            name="Bomba hidráulica",
            code="BOM-001",
            serial_number="SER-BOMBA",
            created_by=user,
        ),
        Equipment.objects.create(
            name="Generador auxiliar",
            code="GEN-002",
            serial_number="SER-GENERADOR",
            status=Equipment.Status.IN_MAINTENANCE,
            created_by=user,
        ),
        Equipment.objects.create(
            name="Tablero eléctrico",
            code="TAB-003",
            serial_number="SER-TABLERO",
            status=Equipment.Status.OUT_OF_SERVICE,
            created_by=user,
        ),
    ]


def equipment_queryset(response):
    return response.context["equipments"]


@pytest.mark.django_db
@pytest.mark.parametrize("query", ["bom-001", "BOMBA", "ser-bomba"])
def test_search_matches_code_name_or_serial_number(client, user, equipments, query):
    client.force_login(user)

    response = client.get(reverse("equipment:list"), {"q": query})

    assert response.status_code == 200
    assert list(equipment_queryset(response)) == [equipments[0]]


@pytest.mark.django_db
def test_search_uses_or_across_fields(client, user, equipments):
    client.force_login(user)

    response = client.get(reverse("equipment:list"), {"q": "002"})

    assert list(equipment_queryset(response)) == [equipments[1]]


@pytest.mark.django_db
def test_status_filter_is_exact(client, user, equipments):
    client.force_login(user)

    response = client.get(
        reverse("equipment:list"), {"status": Equipment.Status.IN_MAINTENANCE}
    )

    assert list(equipment_queryset(response)) == [equipments[1]]


@pytest.mark.django_db
def test_search_and_status_filter_can_be_combined(client, user, equipments):
    client.force_login(user)

    response = client.get(
        reverse("equipment:list"),
        {"q": "SER", "status": Equipment.Status.OUT_OF_SERVICE},
    )

    assert list(equipment_queryset(response)) == [equipments[2]]


@pytest.mark.django_db
def test_invalid_status_is_ignored(client, user, equipments):
    client.force_login(user)

    response = client.get(reverse("equipment:list"), {"status": "invalid"})

    assert list(equipment_queryset(response)) == equipments


@pytest.mark.django_db
def test_retired_equipment_can_be_found(client, user):
    retired = Equipment.objects.create(
        name="Bomba retirada",
        code="RET-001",
        serial_number="SER-RETIRADA",
        status=Equipment.Status.RETIRED,
        created_by=user,
    )
    client.force_login(user)

    response = client.get(reverse("equipment:list"), {"q": "retirada"})

    assert list(equipment_queryset(response)) == [retired]


@pytest.mark.django_db
def test_filters_are_preserved_in_pagination_links(client, user):
    Equipment.objects.bulk_create(
        [
            Equipment(
                name=f"Bomba {number:02}",
                code=f"BOM-{number:02}",
                created_by=user,
            )
            for number in range(1, 22)
        ]
    )
    client.force_login(user)

    response = client.get(reverse("equipment:list"), {"q": "bomba", "page": 2})

    assert response.status_code == 200
    assert len(equipment_queryset(response)) == 1
    assert "q=bomba&amp;page=1" in response.content.decode()
