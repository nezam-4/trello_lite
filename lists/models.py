from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class List(models.Model):
    title = models.CharField(max_length=255)
    board = models.ForeignKey('boards.Board', on_delete=models.CASCADE, related_name='lists')
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'created_at']
        unique_together = ['board', 'position']
    
    def clean(self):
        """Validate constraints before saving"""
        if not self.pk:  # Only for new list
            max_lists = getattr(settings, 'MAX_LISTS_PER_BOARD', 20)
            board_lists_count = List.objects.filter(board=self.board).count()
            
            if board_lists_count >= max_lists:
                raise ValidationError(
                    'Each board cannot have more than {} lists.'.format(max_lists)
                )
    
    def save(self, *args, **kwargs):
        if not self.position:
            # Determine next position
            last_position = List.objects.filter(board=self.board).aggregate(
                models.Max('position')
            )['position__max']
            self.position = (last_position or 0) + 1
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def move_to_position(self, new_position):
        """Move list to a new position"""
        old_position = self.position
        if old_position == new_position:
            return
        
        # Shift other lists
        if new_position > old_position:
            List.objects.filter(
                board=self.board,
                position__gt=old_position,
                position__lte=new_position
            ).update(position=models.F('position') - 1)
        else:
            List.objects.filter(
                board=self.board,
                position__gte=new_position,
                position__lt=old_position
            ).update(position=models.F('position') + 1)
        
        self.position = new_position
        self.save(update_fields=['position'])
    
    @property
    def tasks_count(self):
        """Number of tasks in this list"""
        return self.tasks.count()
    
    def __str__(self):
        return f"{self.board.title} - {self.title}"
