from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """Automatically create a default `Profile` for every newly created `CustomUser`."""
    if created:
        # Create a blank profile instance linked to the new user
        Profile.objects.create(user=instance)
