from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings




@shared_task(bind=True, max_retries=3)
def send_board_invitation_email(self, invitation_id):
    """
    Celery task to send board invitation email
    """
    try:
        from .models import BoardInvitation
        
        invitation = BoardInvitation.objects.get(id=invitation_id)
        
        # Check if invitation is still valid
        if invitation.is_used or invitation.is_expired:
            return f"Invitation {invitation_id} is already used or expired"
        
        # Generate activation link
        activation_link = f"{settings.SITE_URL}/boards/invitations/accept/{invitation.token}/"
        
        # Prepare email context
        context = {
            'board_title': invitation.board.title,
            'board_description': invitation.board.description,
            'invited_by_name': (f"{invitation.invited_by.first_name or ''} {invitation.invited_by.last_name or ''}".strip() or invitation.invited_by.username),
            'role': invitation.role,
            'activation_link': activation_link,
            'expires_at': invitation.expires_at,
        }
        
        # Render email templates
        html_message = render_to_string('emails/board_invitation.html', context)
        plain_message = render_to_string('emails/board_invitation.txt', context)
        
        # Send email
        send_mail(
            subject=f'Invitation to join "{invitation.board.title}" board',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.invited_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f"Email sent successfully to {invitation.invited_email}"
        
    except BoardInvitation.DoesNotExist:
        return f"BoardInvitation with id {invitation_id} does not exist"
        
    except Exception as exc:
        # Retry the task
        raise self.retry(exc=exc, countdown=60, max_retries=3)
