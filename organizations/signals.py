from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OrganizationMembership, default_organization


@receiver(post_save, sender=get_user_model())
def assign_default_organization(sender, instance, created, **kwargs):
    if created:
        OrganizationMembership.objects.get_or_create(
            user=instance, defaults={"organization_id": default_organization()}
        )
