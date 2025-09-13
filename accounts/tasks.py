from celery import shared_task
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from PIL import Image
import io



@shared_task
def create_avatar_thumbnail(profile_id):
    """
    Create thumbnail for avatar asynchronously
    """
    from .models import Profile
    
    try:
        profile = Profile.objects.get(id=profile_id)
        
        if not profile.avatar:
            return _("No avatar found for profile {}").format(profile_id)
            
        # Open the image
        image = Image.open(profile.avatar)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Create thumbnail (150x150 pixels)
        thumbnail_size = (150, 150)
        image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        
        # Create a square thumbnail by cropping/padding
        thumb_image = Image.new('RGB', thumbnail_size, (255, 255, 255))
        
        # Calculate position to center the image
        x = (thumbnail_size[0] - image.size[0]) // 2
        y = (thumbnail_size[1] - image.size[1]) // 2
        thumb_image.paste(image, (x, y))
        
        # Save to BytesIO
        thumb_io = io.BytesIO()
        thumb_image.save(thumb_io, format='JPEG', quality=85)
        thumb_io.seek(0)
        
        # Generate thumbnail path
        thumbnail_path = profile.get_thumbnail_path()
        
        # Save the thumbnail alongside the original avatar
        default_storage.save(thumbnail_path, thumb_io)
        
        return _("Thumbnail created successfully for profile {}").format(profile_id)
        
    except Profile.DoesNotExist:
        return _("Profile {} not found").format(profile_id)
    except Exception as e:
        return _("Error creating thumbnail for profile {}: {}").format(profile_id, str(e))


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, reset_link):
    """
    Celery task to send password reset email with a pre-built reset link
    """
    try:
        from .models import CustomUser
        # Allow inactive users as well; they may use password reset to activate their account
        user = CustomUser.objects.get(pk=user_id)

        context = {
            'user': user,
            'reset_link': reset_link,
            'site_link': settings.SITE_URL,
        }

        subject = _("Password reset requested")
        plain_message = render_to_string('emails/password_reset.txt', context)
        html_message = render_to_string('emails/password_reset.html', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return _("Password reset email sent to %(email)s") % {'email': user.email}
    except CustomUser.DoesNotExist:
        return _("User not found for password reset")
    except Exception as exc:
        # Retry the task on transient errors
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_email_verification(self, user_id, verification_link):
    """
    Celery task to send email verification email with a pre-built verification link
    """
    try:
        from .models import CustomUser
        user = CustomUser.objects.get(pk=user_id)

        context = {
            'user': user,
            'verification_link': verification_link,
            'site_link': settings.SITE_URL,
        }

        subject = _("Verify your email address")
        plain_message = render_to_string('emails/email_verification.txt', context)
        html_message = render_to_string('emails/email_verification.html', context)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return _("Email verification sent to %(email)s") % {'email': user.email}
    except CustomUser.DoesNotExist:
        return _("User not found for email verification")
    except Exception as exc:
        # Retry the task on transient errors
        raise self.retry(exc=exc, countdown=60)
