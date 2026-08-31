from django.db.models.deletion import ProtectedError
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from equipment.models import Equipment


@receiver(pre_delete, sender=Equipment)
def prevent_equipment_deletion(sender, instance, **kwargs):
    raise ProtectedError(
        "Los equipos no se pueden eliminar.",
        {instance},
    )
