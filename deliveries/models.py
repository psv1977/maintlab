from django.conf import settings
from django.db import models

from equipment.models import Equipment
from maintenance.models import WorkOrder
from organizations.models import Organization, default_organization


class Delivery(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        DELIVERED = "delivered", "Entregado"
        RETURNED = "returned", "Recibido"

    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="deliveries", default=default_organization)
    equipment = models.ForeignKey(
        Equipment, on_delete=models.PROTECT, related_name="deliveries"
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.PROTECT,
        related_name="deliveries",
        null=True,
        blank=True,
    )
    client_name = models.CharField(max_length=200)
    client_rut = models.CharField(max_length=20, db_index=True)
    delivered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="deliveries_made",
    )
    received_by = models.CharField(max_length=200)
    delivered_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="deliveries_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-delivered_at"]
        verbose_name = "entrega"
        verbose_name_plural = "entregas"

    def __str__(self):
        return f"{self.equipment} - {self.client_name}"
