from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PasswordHistory


@receiver(post_save, sender=User)
def store_initial_password(sender, instance, created, **kwargs):
    if created and instance.has_usable_password():
        PasswordHistory.objects.create(user=instance, password=instance.password)
