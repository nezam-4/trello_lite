from django.db import models

class List(models.Model):
    title = models.CharField(max_length=255)
    board = models.ForeignKey('boards.Board', on_delete=models.CASCADE, related_name='lists')
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    color = models.CharField(max_length=20, default='blue')
    
    class Meta:
        ordering = ['position', 'created_at']
        unique_together = ['board', 'position']
    
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
        """Move list to a new position using high temporary positions to avoid constraint violations"""
        old_position = self.position
        if old_position == new_position:
            return
        
        # Use a transaction to ensure atomicity
        from django.db import transaction
        
        with transaction.atomic():
            # Find a safe temporary position (higher than any existing position)
            max_position = List.objects.filter(board=self.board).aggregate(
                models.Max('position')
            )['position__max'] or 0
            temp_position = max_position + 1000  # Use a high temporary position
            
            # Step 1: Move this list to temporary position to avoid conflicts
            self.position = temp_position
            self.save(update_fields=['position'])
            
            # Step 2: Shift other lists
            if new_position > old_position:
                # Moving down: shift lists up (decrease their positions)
                List.objects.filter(
                    board=self.board,
                    position__gt=old_position,
                    position__lte=new_position
                ).update(position=models.F('position') - 1)
            else:
                # Moving up: shift lists down (increase their positions)
                List.objects.filter(
                    board=self.board,
                    position__gte=new_position,
                    position__lt=old_position
                ).update(position=models.F('position') + 1)
            
            # Step 3: Move this list to its final position
            self.position = new_position
            self.save(update_fields=['position'])
    
    @property
    def tasks_count(self):
        """Number of tasks in this list"""
        return self.tasks.count()
    
    def __str__(self):
        return f"{self.board.title} - {self.title}"
