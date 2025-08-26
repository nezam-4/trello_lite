from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
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
    avatar=models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio=models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    preferred_language = models.CharField(max_length=10, default='en')
    
    def __str__(self):
        return f"{self.user.username} Profile"
