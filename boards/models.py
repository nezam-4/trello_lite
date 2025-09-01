from django.db import models
from django.utils import timezone
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta
class Board(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    color = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField('accounts.CustomUser', related_name='member_boards', through='BoardMembership',through_fields=('board', 'user'))
    is_public = models.BooleanField(default=False, verbose_name="Public")

    def clean(self):
        """Validate constraints before saving"""
        super().clean()
        # Check user board count limit
        if not self.pk:  # Only for creating a new board
            max_boards = getattr(settings, 'MAX_BOARDS_PER_USER', 10)
            user_boards_count = Board.objects.filter(owner=self.owner).count()
            
            if user_boards_count >= max_boards:
                raise ValidationError(
                    f'You cannot create more than {max_boards} boards.'
                )
    
    @property
    def active_members_count(self):
        """Number of active board members"""
        return self.memberships.filter(status='accepted').count()

    @property
    def active_members(self):
        """QuerySet of accepted board members"""
        return self.memberships.filter(status='accepted')

    def can_add_member(self):
        """Check if a new member can be added"""
        max_members = getattr(settings, 'MAX_MEMBERS_PER_BOARD', 50)
        return self.active_members_count < max_members
    
    def add_member(self, user, invited_by, role='member'):
        """
        this must be update for 'this cant be assing user with out ther permsion  user must accept
        Add a user to the board directly as an accepted member whit membership model.
        Raises ValidationError if constraints are violated.
        """

        # بررسی تعداد اعضای بورد
        max_members = getattr(settings, 'MAX_MEMBERS_PER_BOARD', 50)
        if self.active_members_count >= max_members:
            raise ValidationError(f"This board cannot have more than {max_members} members.")

        # بررسی تعداد Membership های کاربر
        max_memberships = getattr(settings, 'MAX_MEMBERSHIPS_PER_USER', 20)
        user_memberships_count = BoardMembership.objects.filter(user=user, status='accepted').count()
        if user_memberships_count >= max_memberships:
            raise ValidationError(f"{user.username} has reached the membership limit of {max_memberships} boards.")

        # بررسی اینکه کاربر قبلاً عضو نبوده
        if BoardMembership.objects.filter(board=self, user=user).exists():
            raise ValidationError(f"{user.username} is already a member of this board.")

        # ایجاد Membership
        membership = BoardMembership.objects.create(
            board=self,
            user=user,
            role=role,
            invited_by=invited_by,
            status='Pending',
            response_at=timezone.now()
        )

        return membership

    def invite_member(self,invited_email,invited_by,role='member'):
        # create board invitation and signal send email
        BoardInvitation.objects.create(
            board=self,
            invited_email=invited_email,
            role=role,
            invited_by=invited_by,
            expires_at=timezone.now() + timedelta(days=7)
        )

 
class BoardMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    board = models.ForeignKey('boards.Board', on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invited_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='sent_invitations')
    response_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['board', 'user']


    def clean(self):
        """Validate constraints before saving"""
        super().clean()

        # Enforce limits only when membership is (or will become) active
        if self.status == 'accepted':
            max_members = getattr(settings, 'MAX_MEMBERS_PER_BOARD', 50)
            max_memberships = getattr(settings, 'MAX_MEMBERSHIPS_PER_USER', 20)

            board_members_count = BoardMembership.objects.filter(
                board=self.board,
                status='accepted'
            ).exclude(pk=self.pk).count()
            if board_members_count >= max_members:
                raise ValidationError(
                    f'This board cannot have more than {max_members} members.'
                )

            user_memberships_count = BoardMembership.objects.filter(
                user=self.user,
                status='accepted'
            ).exclude(pk=self.pk).count()
            if user_memberships_count >= max_memberships:
                raise ValidationError(
                    f'You cannot be a member of more than {max_memberships} boards.'
                )
    
    def accept(self):
        """Accept membership invitation :user call this"""
        # Check constraints before accepting invitation
        max_members = getattr(settings, 'MAX_MEMBERS_PER_BOARD', 50)
        max_memberships = getattr(settings, 'MAX_MEMBERSHIPS_PER_USER', 20)
        
        # Check board member limit
        board_members_count = BoardMembership.objects.filter(
            board=self.board,
            status='accepted'
        ).count()
        
        if board_members_count >= max_members:
            raise ValidationError(
                f'This board has reached the limit of {max_members} members.'
            )
        
        # Check user membership limit
        user_memberships_count = BoardMembership.objects.filter(
            user=self.user,
            status='accepted'
        ).exclude(pk=self.pk).count()
        
        if user_memberships_count >= max_memberships:
            raise ValidationError(
                f'You have reached the membership limit of {max_memberships}.'
            )
        
        self.status = 'accepted'
        self.response_at = timezone.now()
        self.save()
    
    def reject(self):
        """Reject membership invitation"""
        self.status = 'rejected'
        self.response_at = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.board.title} ({self.get_role_display()})"


class BoardInvitation(models.Model):# invitation with email
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    # use signal whene this model created to send invitation email
    board = models.ForeignKey('boards.Board', on_delete=models.CASCADE, related_name='invitations')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='received_invitations', null=True, blank=True)
    invited_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='created_invitations')
    invited_email = models.EmailField()
    description = models.TextField(null=True, blank=True)
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Validate constraints before sending invitation"""
        super().clean()
        if not self.pk:  # Only for new invitation
            # Check board member limit
            max_members = getattr(settings, 'MAX_MEMBERS_PER_BOARD', 50)
            board_members_count = BoardMembership.objects.filter(
                board=self.board,
                status='accepted'
            ).count()
            
            if board_members_count >= max_members:
                raise ValidationError(
                    f'This board has reached the limit of {max_members} members and cannot send new invitations.'
                )
    
    @property
    def is_expired(self):
        """Check if the invitation is expired"""
        return timezone.now() > self.expires_at
      
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invitation for {self.invited_email} to {self.board.title}"

    class Meta:
        unique_together = ['board', 'invited_email']

class BoardActivity(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('join', 'Join'),
        ('leave', 'Leave'),
    ]
    
    board = models.ForeignKey('boards.Board', on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='create')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='board_activities',blank=True,null=True)
    description = models.TextField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
       

    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} {self.board.title}"
