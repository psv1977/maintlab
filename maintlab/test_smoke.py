"""Prueba temporal de infraestructura; se elimina al crear el modelo Equipment."""

import pytest
from django.db import connection


@pytest.mark.django_db
def test_uses_in_memory_sqlite_database():
    assert connection.vendor == "sqlite"
    assert connection.settings_dict["NAME"].startswith("file:memorydb_")
