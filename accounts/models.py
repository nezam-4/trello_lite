from django.db import models
from django.contrib.auth.models import AbstractUser
from boards.models import Board
from django.utils import timezone
from django.core.files.storage import default_storage
from PIL import Image
import uuid
import os
import io

def avatar_upload_path(instance, filename):
    """Save avatars under avatar/<MM>/filename"""
    month = timezone.now().strftime("%m")
    ext = os.path.splitext(filename)[1]
    random_suffix = uuid.uuid4().hex[:8]
    new_filename = f"user_{instance.user.id}_{random_suffix}{ext}"
    return f"avatar/{month}/{new_filename}"

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    def get_boards_count(self):
        """Number of boards owned by the user"""
        return self.owned_boards.count()
    
    def get_memberships_count(self):
        """Number of board memberships of the user"""
        return self.memberships.filter(status='accepted').count()

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
    user=models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='profile')
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    bio=models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    preferred_language = models.CharField(max_length=10, default='en')
    
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
