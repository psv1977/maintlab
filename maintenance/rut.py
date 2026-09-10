import re

from django.core.exceptions import ValidationError


def normalize_rut(value):
    compact_rut = re.sub(r"[^0-9kK]", "", value or "").upper()
    if len(compact_rut) < 2 or not compact_rut[:-1].isdigit():
        raise ValidationError("Ingrese un RUT chileno válido.")

    number, verifier = compact_rut[:-1].lstrip("0") or "0", compact_rut[-1]
    total = sum(
        int(digit) * factor
        for digit, factor in zip(reversed(number), [2, 3, 4, 5, 6, 7] * 2)
    )
    expected_verifier = "0123456789K"[(-total) % 11]
    if verifier != expected_verifier:
        raise ValidationError("El dígito verificador del RUT no coincide.")

    grouped_number = f"{int(number):,}".replace(",", ".")
    return f"{grouped_number}-{verifier}"
