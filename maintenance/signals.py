from django.db.models.deletion import ProtectedError
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from maintenance.models import MaintenanceRecord, WorkOrder


@receiver(pre_delete, sender=MaintenanceRecord)
def prevent_maintenance_deletion(sender, instance, **kwargs):
    raise ProtectedError(
        "Los registros de mantenimiento no se pueden eliminar.",
        {instance},
    )


@receiver(pre_delete, sender=WorkOrder)
def prevent_work_order_deletion(sender, instance, **kwargs):
    raise ProtectedError(
        "Las órdenes de trabajo no se pueden eliminar.",
        {instance},
    )
