from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _




@shared_task(bind=True, max_retries=3)
def send_registered_invitation_email(self, invitation_id):
    """
    Celery task to notify a *registered* user about a board invitation.
    Email simply informs the user to check their dashboard.
    """
    try:
        from .models import BoardInvitation
        invitation = BoardInvitation.objects.get(id=invitation_id)

        # Only proceed if invitation still valid and linked to a user
        if invitation.is_used or invitation.is_expired or invitation.user is None:
            return _("Invalid or unusable invitation")

        site_link = settings.SITE_URL
        user = invitation.user
        plain_message = _(
            "Hi %(name)s,\n\n"
            "You have a new invitation to join the board '%(board_title)s'.\n\n"
            "Please log in to your dashboard (%(site_link)s) to accept or reject the invitation.\n\n"
            "Regards,\n%(invited_by)s"
        ) % {
            'name': user.first_name or user.username,
            'board_title': invitation.board.title,
            'site_link': site_link,
            'invited_by': invitation.invited_by.username
        }
        html_message = render_to_string('emails/board_invitation_registered.html', {
            'user': user,
            'board_title': invitation.board.title,
            'site_link': site_link,
            'invited_by_name': invitation.invited_by.username,
        })
        send_mail(
            subject=_("New board invitation: %(board_title)s") % {'board_title': invitation.board.title},
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return _("Notification sent")
    except BoardInvitation.DoesNotExist:
        return _("Invitation does not exist")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)


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
            return _("Invitation %(invitation_id)s is already used or expired") % {'invitation_id': invitation_id}
        
        # Site link (homepage)
        site_link = settings.SITE_URL

        # Prepare email context
        context = {
            'board_title': invitation.board.title,
            'board_description': invitation.board.description,
            'invited_by_name': (f"{invitation.invited_by.first_name or ''} {invitation.invited_by.last_name or ''}".strip() or invitation.invited_by.username),
            'role': invitation.role,
            'site_link': site_link,
            'expires_at': invitation.expires_at,
        }
        
        # Render email templates
        html_message = render_to_string('emails/board_invitation.html', context)
        plain_message = render_to_string('emails/board_invitation.txt', context)
        
        # Send email
        send_mail(
            subject=_("Invitation to join \"%(board_title)s\" board") % {'board_title': invitation.board.title},
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.invited_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return _("Email sent successfully to %(email)s") % {'email': invitation.invited_email}
        
    except BoardInvitation.DoesNotExist:
        return _("BoardInvitation with id %(invitation_id)s does not exist") % {'invitation_id': invitation_id}
        
    except Exception as exc:
        # Retry the task
        raise self.retry(exc=exc, countdown=60, max_retries=3)
