from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta


# Default expiration for board invitations (7 days from creation)

def default_invitation_expiry():
    """Return datetime 7 days from now for invitation expiration"""
    return timezone.now() + timedelta(days=7)


class Board(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=500,null=True,blank=True)
    color = models.CharField(max_length=7,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField('accounts.CustomUser', related_name='member_boards', through='BoardMembership',through_fields=('board', 'user'))
    is_public = models.BooleanField(default=False, verbose_name=_("Public"))

    def clean(self):
        """Validate constraints before saving"""
        super().clean()
        # Check user board count limit
        if not self.pk:  # Only for creating a new board
            max_boards = getattr(settings, 'MAX_BOARDS_PER_USER', 10)
            user_boards_count = Board.objects.filter(owner=self.owner).count()
            
            if user_boards_count >= max_boards:
                raise ValidationError(
                    _("You cannot create more than %(max_boards)s boards.") % {'max_boards': max_boards}
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
            raise ValidationError(_("This board cannot have more than %(max_members)s members.") % {'max_members': max_members})

        # بررسی تعداد Membership های کاربر
        max_memberships = getattr(settings, 'MAX_MEMBERSHIPS_PER_USER', 20)
        user_memberships_count = BoardMembership.objects.filter(user=user, status='accepted').count()
        if user_memberships_count >= max_memberships:
            raise ValidationError(_("%(username)s has reached the membership limit of %(max_memberships)s boards.") % {'username': user.username, 'max_memberships': max_memberships})

        # بررسی اینکه کاربر قبلاً عضو نبوده
        if BoardMembership.objects.filter(board=self, user=user).exists():
            raise ValidationError(_("%(username)s is already a member of this board.") % {'username': user.username})

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
        ('admin', _("Admin")),
        ('member', _("Member")),
    ]
    
    STATUS_CHOICES = [
        ('pending', _("Pending")),
        ('accepted', _("Accepted")),
        ('rejected', _("Rejected")),
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
                    _("This board cannot have more than %(max_members)s members.") % {'max_members': max_members}
                )

            user_memberships_count = BoardMembership.objects.filter(
                user=self.user,
                status='accepted'
            ).exclude(pk=self.pk).count()
            if user_memberships_count >= max_memberships:
                raise ValidationError(
                    _("You cannot be a member of more than %(max_memberships)s boards.") % {'max_memberships': max_memberships}
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
                _("This board has reached the limit of %(max_members)s members.") % {'max_members': max_members}
            )
        
        # Check user membership limit
        user_memberships_count = BoardMembership.objects.filter(
            user=self.user,
            status='accepted'
        ).exclude(pk=self.pk).count()
        
        if user_memberships_count >= max_memberships:
            raise ValidationError(
                _("You have reached the membership limit of %(max_memberships)s.") % {'max_memberships': max_memberships}
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
        return _("%(username)s - %(board_title)s (%(role)s)") % {
            'username': self.user.username,
            'board_title': self.board.title,
            'role': self.get_role_display()
        }


class BoardInvitation(models.Model):# invitation with email
    ROLE_CHOICES = [
        ('admin', _("Admin")),
        ('member', _("Member")),
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

    # Invitation status management
    STATUS_CHOICES = [
        ('pending', _("Pending")),
        ('accepted', _("Accepted")),
        ('rejected', _("Rejected")),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField(default=default_invitation_expiry)
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
                    _("This board has reached the limit of %(max_members)s members and cannot send new invitations.") % {'max_members': max_members}
                )
    
    @property
    def is_expired(self):
        """Check if the invitation is expired"""
        return timezone.now() > self.expires_at
      
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return _("Invitation for %(email)s to %(board_title)s") % {
            'email': self.invited_email,
            'board_title': self.board.title
        }

    class Meta:
        unique_together = ['board', 'invited_email']

class BoardActivity(models.Model):
    ACTION_CHOICES = [
        ('create', _("Create")),
        ('update', _("Update")),
        ('delete', _("Delete")),
        ('join', _("Join")),
        ('leave', _("Leave")),
        ('reject', _("Reject")),
        ('accept', _("Accept")),
        ('invite', _("Invite"))
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
        return _("%(username)s %(action)s %(board_title)s") % {
            'username': self.user.username,
            'action': self.get_action_display(),
            'board_title': self.board.title
        }
