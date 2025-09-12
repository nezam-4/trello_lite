from django.db import models
from django.utils.translation import gettext_lazy as _

class List(models.Model):
    title = models.CharField(max_length=255)
    board = models.ForeignKey('boards.Board', on_delete=models.CASCADE, related_name='lists')
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    color = models.CharField(max_length=20, default='blue')
    
    class Meta:
        ordering = ['position', 'created_at']

    
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
        """Move list to a new position safely on SQLite/SQLite-like DBs.

        This implementation avoids transient UNIQUE(board, position) conflicts by:
        1) Temporarily moving the current list to a high position out of the active range
        2) Shifting affected sibling rows one-by-one in a safe order
        3) Placing the current list at its final position
        """
        old_position = self.position
        # Clamp to at least 1 early
        if new_position < 1:
            new_position = 1
        if old_position == new_position:
            return
        
        # Use a transaction to ensure atomicity
        from django.db import transaction
        
        with transaction.atomic():
            # Determine bounds and a safe temporary position (higher than any existing position)
            board_qs = List.objects.filter(board=self.board)
            total_lists = board_qs.count()
            # Clamp to the end of the board
            if new_position > total_lists:
                new_position = total_lists
            max_position = board_qs.aggregate(models.Max('position'))['position__max'] or 0
            temp_position = max_position + 1000  # Use a high temporary position
            
            # Step 1: Move this list to a temporary position
            self.position = temp_position
            self.save(update_fields=['position'])
            
            # Step 2: Shift other lists without violating UNIQUE(board, position)
            if new_position > old_position:
                # Moving down: shift lists up (decrease their positions)
                affected_ids = (board_qs
                                .filter(position__gt=old_position, position__lte=new_position)
                                .order_by('position')
                                .values_list('pk', flat=True))
                for pk in affected_ids:
                    # Update each row individually to avoid transient duplicates
                    List.objects.filter(pk=pk).update(position=models.F('position') - 1)
            else:
                # Moving up: shift lists down (increase their positions)
                affected_ids = (board_qs
                                .filter(position__gte=new_position, position__lt=old_position)
                                .order_by('-position')
                                .values_list('pk', flat=True))
                for pk in affected_ids:
                    # Update each row individually to avoid transient duplicates
                    List.objects.filter(pk=pk).update(position=models.F('position') + 1)
            
            # Step 3: Place this list at its final position
            self.position = new_position
            self.save(update_fields=['position'])
    
    @property
    def tasks_count(self):
        """Number of tasks in this list"""
        return self.tasks.count()
    
    def __str__(self):
        return _("%(board_title)s - %(list_title)s") % {
            'board_title': self.board.title,
            'list_title': self.title
        }
