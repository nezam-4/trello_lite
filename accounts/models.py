from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

from django.utils import timezone
import uuid
import os


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
    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    def get_boards_count(self):
        """Number of boards owned by the user"""
        return self.owned_boards.count()
    
    def get_memberships_count(self):
        """Number of board memberships of the user"""
        return self.board_memberships.filter(status='accepted').count()

    def __str__(self):
        return self.username

class Profile(models.Model):
    user=models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='profile')
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    bio=models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    preferred_language = models.CharField(max_length=10, default='en')
    
    def __str__(self):
        return f"{self.user.username} Profile"
