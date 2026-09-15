from datetime import date, datetime
from io import BytesIO

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from openpyxl import Workbook

from equipment.models import Equipment


@pytest.fixture
def staff_user():
    return User.objects.create_user(username="staff", password="test1234", is_staff=True)


@pytest.mark.django_db
def test_import_csv_creates_equipment_with_optional_fields(client, staff_user):
    client.force_login(staff_user)
    content = (
        "name,code,equipment_type,location,commissioned_at,status\n"
        "Camión de servicio,CAM-001,automotive,Flota,2024-05-10,in_maintenance\n"
    ).encode()
    uploaded_file = SimpleUploadedFile("equipos.csv", content, content_type="text/csv")

    response = client.post(reverse("equipment:import"), {"file": uploaded_file})

    assert response.status_code == 200
    assert response.context["imported_count"] == 1
    equipment = Equipment.objects.get(code="CAM-001")
    assert equipment.equipment_type == Equipment.EquipmentType.AUTOMOTIVE
    assert equipment.location.name == "Flota"
    assert equipment.commissioned_at == date(2024, 5, 10)
    assert equipment.status == Equipment.Status.IN_MAINTENANCE


@pytest.mark.django_db
def test_import_xlsx_accepts_excel_datetime(client, staff_user):
    client.force_login(staff_user)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["name", "code", "commissioned_at"])
    worksheet.append(["Compresor", "COMP-001", datetime(2023, 8, 15)])
    content = BytesIO()
    workbook.save(content)
    uploaded_file = SimpleUploadedFile(
        "equipos.xlsx",
        content.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    response = client.post(reverse("equipment:import"), {"file": uploaded_file})

    assert response.status_code == 200
    assert Equipment.objects.get(code="COMP-001").commissioned_at == date(2023, 8, 15)


@pytest.mark.django_db
def test_import_rejects_invalid_date_without_creating_rows(client, staff_user):
    client.force_login(staff_user)
    content = b"name,code,commissioned_at\nCompresor,COMP-001,15/08/2023\n"
    uploaded_file = SimpleUploadedFile("equipos.csv", content, content_type="text/csv")

    response = client.post(reverse("equipment:import"), {"file": uploaded_file})

    assert response.status_code == 200
    assert response.context["errors"] == [
        "Fila 2: commissioned_at debe usar el formato YYYY-MM-DD."
    ]
    assert not Equipment.objects.exists()
