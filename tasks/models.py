from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


def get_default_due_date():
    """Return default due date: 7 days from now"""
    return timezone.now().date() + timedelta(days=7)


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True,null=True)
    list = models.ForeignKey('lists.List', on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ManyToManyField('accounts.CustomUser', blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='created_tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True, default=get_default_due_date)
    position = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'created_at']
        unique_together = ['list', 'position']
    
    def clean(self):
        """Validate constraints before saving"""
        # Skip validation for new objects that haven't been saved yet
        if not self.pk:
            return

        # Ensure all assigned users are members of the board
        board = self.list.board
        invalid_users = [user for user in self.assigned_to.all() if not board.active_members.filter(user_id=user.id).exists()]
        if invalid_users:
            raise ValidationError('All assigned users must be members of this board.')
    
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
    
    def move_to_list(self, new_list, new_position=None):
        """Move task to a new list"""
        old_list = self.list
        old_position = self.position
        
        # Ensure the new list belongs to the same board
        if new_list.board != old_list.board:
            raise ValidationError('Cannot move task to a list of another board.')
        
        # Remove from previous position
        Task.objects.filter(
            list=old_list,
            position__gt=old_position
        ).update(position=models.F('position') - 1)
        
        # Determine new position
        if new_position is None:
            last_position = Task.objects.filter(list=new_list).aggregate(
                models.Max('position')
            )['position__max']
            new_position = (last_position or 0) + 1
        else:
            # Shift existing tasks
            Task.objects.filter(
                list=new_list,
                position__gte=new_position
            ).update(position=models.F('position') + 1)
        
        self.list = new_list
        self.position = new_position
        self.save(update_fields=['list', 'position'])
    
    def move_to_position(self, new_position):
        """Move task within the same list"""
        old_position = self.position
        if old_position == new_position:
            return
        
        # Shift other tasks
        if new_position > old_position:
            Task.objects.filter(
                list=self.list,
                position__gt=old_position,
                position__lte=new_position
            ).update(position=models.F('position') - 1)
        else:
            Task.objects.filter(
                list=self.list,
                position__gte=new_position,
                position__lt=old_position
            ).update(position=models.F('position') + 1)
        
        self.position = new_position
        self.save(update_fields=['position'])
    
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
        return f"{self.list.title} - {self.title}"


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
            raise ValidationError('Only board members can comment.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title}"
