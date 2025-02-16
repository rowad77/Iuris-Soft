from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from accounts.models import Client, Profile
from utils.enum import UserType

User = get_user_model()

@receiver(post_save, sender=User)
def create_client_for_user(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)
    
    if created and instance.user_type == UserType.CLIENT:
        Client.objects.create(user=instance)