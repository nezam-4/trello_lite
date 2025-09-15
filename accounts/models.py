from django.db import models
from django.contrib.auth.models import AbstractUser
from boards.models import Board
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
import os
import secrets

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        # Regular users are inactive by default
        extra_fields.setdefault('is_active', False)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Superusers are active by default
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

def avatar_upload_path(instance, filename):
    """Save avatars under avatar/<MM>/filename"""
    month = timezone.now().strftime("%m")
    ext = os.path.splitext(filename)[1]
    random_suffix = uuid.uuid4().hex[:8]
    new_filename = f"user_{instance.user.id}_{random_suffix}{ext}"
    return f"avatar/{month}/{new_filename}"

class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150, 
        unique=True,
        verbose_name=_('Username'),
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_('Email address'),
        help_text=_('Required. Enter a valid email address.')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
        help_text=_('Date and time when the user was created')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at'),
        help_text=_('Date and time when the user was last updated')
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('Active'),
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    )
    email_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Email verified at'),
        help_text=_('Date and time when the email was verified')
    )
    email_verification_token = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name=_('Email verification token'),
        help_text=_('Token used for email verification')
    )
    email_verification_token_created_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Verification token created at'),
        help_text=_('Date and time when verification token was created')
    )
    first_name = models.CharField(
        max_length=150, 
        blank=True, 
        null=True,
        verbose_name=_('First name'),
        help_text=_('User\'s first name')
    )
    last_name = models.CharField(
        max_length=150, 
        blank=True, 
        null=True,
        verbose_name=_('Last name'),
        help_text=_('User\'s last name')
    )
    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def get_boards_count(self):
        """Number of boards owned by the user"""
        return self.owned_boards.count()
    
    def get_memberships_count(self):
        """Number of board memberships of the user"""
        return self.memberships.filter(status='accepted').count()
    
    def generate_verification_token(self):
        """Generate a new email verification token"""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_token_created_at = timezone.now()
        self.save(update_fields=['email_verification_token', 'email_verification_token_created_at'])
        return self.email_verification_token
    
    def is_verification_token_valid(self, token, expiry_hours=24):
        """Check if verification token is valid and not expired"""
        if not self.email_verification_token or not self.email_verification_token_created_at:
            return False
        
        if self.email_verification_token != token:
            return False
        
        expiry_time = self.email_verification_token_created_at + timezone.timedelta(hours=expiry_hours)
        return timezone.now() < expiry_time
    
    def verify_email(self):
        """Mark email as verified and activate user"""
        self.email_verified_at = timezone.now()
        self.is_active = True
        self.email_verification_token = None
        self.email_verification_token_created_at = None
        self.save(update_fields=['email_verified_at', 'is_active', 'email_verification_token', 'email_verification_token_created_at'])
    
    @property
    def is_email_verified(self):
        """Check if email is verified"""
        return self.email_verified_at is not None
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'accounts_customuser'

    @property
    def all_boards(self):
        owned = self.owned_boards.all()
        member = Board.objects.filter(
            memberships__user=self,
            memberships__status='accepted'
        )
        return (owned | member).distinct()
    def __str__(self):
        return self.username

class Profile(models.Model):
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fa', _('Persian')),
    ]
    
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User'),
        help_text=_('The user this profile belongs to')
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path, 
        blank=True, 
        null=True,
        verbose_name=_('Avatar'),
        help_text=_('User profile picture')
    )
    bio = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Biography'),
        help_text=_('Tell us about yourself')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
        help_text=_('Date and time when the profile was created')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at'),
        help_text=_('Date and time when the profile was last updated')
    )
    preferred_language = models.CharField(
        max_length=10, 
        default='en',
        choices=LANGUAGE_CHOICES,
        verbose_name=_('Preferred language'),
        help_text=_('Your preferred language for the interface')
    )
    
    def get_thumbnail_path(self):
        """Get thumbnail path from avatar path by adding _thumbnail before extension"""
        if not self.avatar:
            return None
        
        avatar_path = self.avatar.name
        name, ext = os.path.splitext(avatar_path)
        return f"{name}_thumbnail{ext}"
    
    def save(self, *args, **kwargs):
        # Check if avatar has changed
        avatar_changed = False
        if self.pk:
            try:
                old_profile = Profile.objects.get(pk=self.pk)
                avatar_changed = old_profile.avatar != self.avatar
            except Profile.DoesNotExist:
                avatar_changed = bool(self.avatar)
        else:
            avatar_changed = bool(self.avatar)
        
        super().save(*args, **kwargs)
        
        # Create thumbnail asynchronously if avatar changed
        if avatar_changed and self.avatar:
            from .tasks import create_avatar_thumbnail
            create_avatar_thumbnail.delay(self.id)
    
    def __str__(self):
        return f"{self.user.username} Profile"
    
    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        db_table = 'accounts_profile'
