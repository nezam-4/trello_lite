from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BoardInvitation
from .tasks import send_board_invitation_email

@receiver(post_save, sender=BoardInvitation)
def send_invitation_email_on_create(sender, instance, created, **kwargs):
    """
    Signal to send invitation email when a new BoardInvitation is created
    """
    if created:
        # Trigger Celery task to send email asynchronously
        send_board_invitation_email.delay(instance.id)
