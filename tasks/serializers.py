from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Task, TaskComment
from lists.models import List
from accounts.serializers import ProfileSerializer

User = get_user_model()


class TaskListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing tasks.
    - Used for showing task summaries in list views.
    - Contains main task information + assignee info.
    - Optimized for speed and minimum payload size.
    """
    assigned_to_usernames = serializers.SerializerMethodField()
    assigned_users = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'list',
            'assigned_to_usernames', 'assigned_users',
            'priority', 'due_date', 'position', 'is_completed', 
            'is_overdue', 
        ]


    def get_assigned_to_usernames(self, obj):
        return list(obj.assigned_to.values_list('username', flat=True))
    
    def get_assigned_users(self, obj):
        return [
            {
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name(),
                'initials': self._get_initials(user),
                'profile': ProfileSerializer(user.profile, context=self.context).data if hasattr(user, 'profile') else None
            }
            for user in obj.assigned_to.all()
        ]
    
    def _get_initials(self, user):
        if user.get_full_name():
            return ''.join([p[0] for p in user.get_full_name().split()[:2]]).upper()
        return user.username[:2].upper() if user.username else '??'


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for task detail view.
    - Shows all information of a specific task.
    - Includes full assignee info, comments count.
    - Used on the task details page.
    """
    assigned_to_usernames = serializers.SerializerMethodField()
    assigned_users = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    list_title = serializers.CharField(source='list.title', read_only=True)
    comments_count = serializers.SerializerMethodField()
    board = serializers.IntegerField(source='board.id', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'list', 'list_title',
            'board',
            'assigned_to', 'assigned_to_usernames', 'assigned_users',
            'created_by_username', 'priority', 'due_date', 'position',
            'is_completed', 'completed_at', 'comments_count', 'is_overdue',
            'created_at', 'updated_at'
        ]
    
    def get_assigned_to_usernames(self, obj):
        return list(obj.assigned_to.values_list('username', flat=True))

    def get_assigned_users(self, obj):
        """Get assigned users with profile data"""
        users = obj.assigned_to.all()
        return [{
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name(),
            'initials': ''.join([p[0] for p in user.get_full_name().split()[:2]]).upper() if user.get_full_name() else user.username[:2].upper(),
            'profile': ProfileSerializer(user.profile).data if hasattr(user, 'profile') else None
        } for user in users]

    def get_comments_count(self, obj):
        """Calculate task comments count"""
        return obj.comments.count()


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new task.
    - Validates incoming data to create a task.
    - Automatically assigns the creator.

    """
    
    class Meta:
        model = Task
        fields = ['title', 'list', ]
    
    def validate_list(self, value):
        """Validate that user has access to the list"""
        user = self.context['request'].user
        board = value.board
        
        # Check if user is board member or owner
        if board.owner != user:
            if not board.active_members.filter(user=user).exists():
                raise serializers.ValidationError(
                    _("You don't have access to this list.")
                )
        return value
    
    
    def create(self, validated_data):
        """Automatically set the task creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a task.
    - Used to edit existing task information.
    - Includes only editable fields.
    - Task creator and list cannot be changed via this serializer.
    """
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'due_date', 'is_completed']
    
    def validate_assigned_to(self, value):
        """Validate that assigned users are board members"""
        if value:
            task = self.instance
            board = task.list.board
            invalid_users = [user for user in value if not board.active_members.filter(user=user).exists() and board.owner != user]
            if invalid_users:
                raise serializers.ValidationError(
                    _("All assigned users must be members of this board.")
                )
        return value


class TaskMoveSerializer(serializers.Serializer):
    """
    Serializer for moving tasks.
    - Handles moving tasks between lists or positions.
    """
    new_list = serializers.PrimaryKeyRelatedField(
        queryset=List.objects.all(),
        required=False,
        allow_null=True
    )
    new_position = serializers.IntegerField(required=False, min_value=1)
    
    def validate_new_list(self, value):
        """Validate that user has access to the new list"""
        if value:
            user = self.context['request'].user
            board = value.board
            
            # Check if user is board member or owner
            if board.owner != user:
                if not board.active_members.filter(user=user).exists():
                    raise serializers.ValidationError(
                        _("You don't have access to this list.")
                    )
        return value
    
    def validate(self, attrs):
        """Validate move operation"""
        new_list = attrs.get('new_list')
        new_position = attrs.get('new_position')
        
        if not new_list and not new_position:
            raise serializers.ValidationError(
                _("Either new_list or new_position must be provided.")
            )
        
        return attrs


class TaskCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for task comments.
    - Shows comment information with user details.
    - Used for listing and creating comments.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = [
            'id', 'task', 'task_title', 'user_username', 'user_full_name',
            'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'task']
    
    def validate_task(self, value):
        """Validate that user has access to the task"""
        user = self.context['request'].user
        board = value.list.board
        
        # Check if user is board member or owner
        if board.owner != user:
            if not board.active_members.filter(user=user).exists():
                raise serializers.ValidationError(
                    _("You don't have access to this task.")
                )
        return value
    
    def create(self, validated_data):
        """Automatically set the comment user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskCommentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating task comments.
    - Only allows updating content.
    - User and task cannot be changed.
    """
    
    class Meta:
        model = TaskComment
        fields = ['content']
