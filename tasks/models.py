from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _

def get_default_due_date():
    """Return default due date: 7 days from now"""
    return timezone.now().date() + timedelta(days=7)


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True,null=True)
    list = models.ForeignKey('lists.List', on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ManyToManyField('accounts.CustomUser', blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='created_tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True, default=get_default_due_date)    
    position = models.PositiveIntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'created_at']
    
    def clean(self):
        """Validate constraints before saving"""
        # Skip validation for new objects that haven't been saved yet
        if not self.pk:
            return

        # Ensure all assigned users are members of the board
        board = self.list.board
        invalid_users = [user for user in self.assigned_to.all() if not board.active_members.filter(user_id=user.id).exists()]
        if invalid_users:
            raise ValidationError(_('All assigned users must be members of this board.'))
    
    def save(self, *args, **kwargs):
        if not self.position:
            # Determine next position
            last_position = Task.objects.filter(list=self.list).aggregate(
                models.Max('position')
            )['position__max']
            self.position = (last_position or 0) + 1
        
        # Set completed_at 
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def move_to_position(self, new_position):
        """Move task to a new position within the same list"""
        if new_position < 1:
            new_position = 1
            
        if self.position == new_position:
            return
            
        with transaction.atomic():
            old_position = self.position
            
            if new_position > old_position:
                # Moving down: shift tasks up
                Task.objects.filter(
                    list_id=self.list_id,
                    position__gt=old_position,
                    position__lte=new_position
                ).exclude(id=self.id).update(position=F('position') - 1)
            else:
                # Moving up: shift tasks down
                Task.objects.filter(
                    list_id=self.list_id,
                    position__gte=new_position,
                    position__lt=old_position
                ).exclude(id=self.id).update(position=F('position') + 1)
            
            # Update this task's position
            self.position = new_position
            self.save(update_fields=['position'])

    def move_to_list(self, new_list, new_position=None):
        """Move task to a different list"""
        # Validate same board
        if new_list.board_id != self.list.board_id:
            raise ValidationError(_('Cannot move task between different boards'))
        
        # If same list, just change position
        if self.list_id == new_list.id:
            if new_position is not None:
                self.move_to_position(new_position)
            return
        
        with transaction.atomic():
            old_list_id = self.list_id
            old_position = self.position
            
            # Step 1: Fix old list positions first
            Task.objects.filter(
                list_id=old_list_id,
                position__gt=old_position
            ).update(position=F('position') - 1)
            
            # Step 2: Determine target position in new list
            if new_position is None:
                # Add to end
                last_task = Task.objects.filter(list=new_list).order_by('-position').first()
                target_position = (last_task.position + 1) if last_task else 1
            else:
                target_position = max(1, new_position)
                # Make room in new list
                Task.objects.filter(
                    list=new_list,
                    position__gte=target_position
                ).update(position=F('position') + 1)
            
            # Step 3: Move to new list and position
            self.list = new_list
            self.position = target_position
            self.save(update_fields=['list', 'position'])

    def mark_completed(self):
        """Mark task as completed"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save(update_fields=['is_completed', 'completed_at'])
    
    def mark_incomplete(self):
        """Mark task as incomplete"""
        self.is_completed = False
        self.completed_at = None
        self.save(update_fields=['is_completed', 'completed_at'])
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and not self.is_completed:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def board(self):
        """Access to the board related to this task"""
        return self.list.board
    
    def __str__(self):
        return _("%(list_title)s - %(task_title)s") % {
            'list_title': self.list.title,
            'task_title': self.title
        }


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def clean(self):
        """Validate that the user is a member of the board"""
        if not self.task.board.active_members.filter(id=self.user.id).exists():
            raise ValidationError(_('Only board members can comment.'))
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return _("%(username)s - %(task_title)s") % {
            'username': self.user.username,
            'task_title': self.task.title
        }
