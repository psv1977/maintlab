import pytest
from django.core.exceptions import ValidationError

from maintenance.rut import normalize_rut


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("761234560", "76.123.456-0"),
        ("11.111.111-1", "11.111.111-1"),
        ("12.345.678-5", "12.345.678-5"),
    ],
)
def test_normalize_rut_accepts_valid_values(value, expected):
    assert normalize_rut(value) == expected


@pytest.mark.parametrize("value", ["", "12.345.678-4", "abc"])
def test_normalize_rut_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        normalize_rut(value)
