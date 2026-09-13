from django.conf import settings
from django.db import models
from django.utils import timezone

from organizations.models import Customer, Organization, default_organization


class Location(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="locations", default=default_organization)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["organization", "name"], name="unique_location_name_per_organization")]
        verbose_name = "ubicación"
        verbose_name_plural = "ubicaciones"

    def __str__(self):
        return self.name


class Equipment(models.Model):

    class EquipmentType(models.TextChoices):
        INDUSTRIAL = "industrial", "Industrial"
        AUTOMOTIVE = "automotive", "Automotriz"

    class Status(models.TextChoices):
        OPERATIONAL = "operational", "Operativo"
        IN_MAINTENANCE = "in_maintenance", "En mantenimiento"
        OUT_OF_SERVICE = "out_of_service", "Fuera de servicio"
        RETIRED = "retired", "Retirado"

    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="equipments", default=default_organization)
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="equipments", null=True, blank=True,
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    equipment_type = models.CharField(
        max_length=20,
        choices=EquipmentType.choices,
        default=EquipmentType.INDUSTRIAL,
    )
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="equipments",
        null=True,
        blank=True,
    )
    commissioned_at = models.DateField(null=True, blank=True)
    application = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPERATIONAL,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(class)s_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(class)s_updated",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["organization", "code"], name="unique_equipment_code_per_organization")]
        permissions = [
            ("retire_equipment", "Can retire equipment"),
        ]

    def __str__(self):
        return self.name

    @property
    def measurement_unit(self):
        if self.equipment_type == self.EquipmentType.AUTOMOTIVE:
            return "kilometers"
        return "hours"

    @property
    def measurement_unit_label(self):
        if self.measurement_unit == "kilometers":
            return "Kilometraje"
        return "Horómetro"


class EquipmentIdentifier(models.Model):
    class IdentifierType(models.TextChoices):
        LICENSE_PLATE = "license_plate", "Patente"
        VIN = "vin", "VIN"
        CHASSIS = "chassis", "Chasis"
        ENGINE = "engine", "Número de motor"
        OTHER = "other", "Otro identificador"

    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="equipment_identifiers", default=default_organization)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name="identifiers")
    identifier_type = models.CharField(max_length=20, choices=IdentifierType.choices)
    value = models.CharField(max_length=100)

    class Meta:
        ordering = ["identifier_type", "value"]
        constraints = [models.UniqueConstraint(fields=["organization", "identifier_type", "value"], name="unique_equipment_identifier_per_organization")]
        verbose_name = "identificador de equipo"
        verbose_name_plural = "identificadores de equipo"

    def __str__(self):
        return f"{self.get_identifier_type_display()}: {self.value}"


class MeterReading(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="meter_readings", default=default_organization)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name="meter_readings")
    value = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="meter_readings_recorded",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-recorded_at", "-pk"]
        verbose_name = "lectura de medidor"
        verbose_name_plural = "lecturas de medidores"

    def __str__(self):
        return f"{self.equipment} - {self.value}"
