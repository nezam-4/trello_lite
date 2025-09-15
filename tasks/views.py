from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import Task, TaskComment
from .serializers import (
    TaskListSerializer, TaskDetailSerializer, TaskCreateSerializer,
    TaskUpdateSerializer, TaskMoveSerializer, TaskCommentSerializer,
    TaskCommentUpdateSerializer
)
from lists.models import List
from boards.models import Board, BoardMembership

User = get_user_model()


class TaskListView(APIView):
    """
    View for listing tasks in a specific list or creating new tasks.
    
    Behaviour:
    - GET: Return all tasks in the specified list.
    - POST: Create a new task in the specified list.
    - Only board members can access tasks.
    - Tasks are ordered by position.
    
    Endpoint: GET/POST /api/v1/lists/{list_id}/tasks/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_list_with_access_check(self, list_id, user):
        """Get list and verify user has access to it"""
        try:
            list_obj = List.objects.get(id=list_id)
            board = list_obj.board
            
            # Check if user is board owner or member
            if board.owner != user:
                if not board.active_members.filter(user=user).exists():
                    raise PermissionDenied(_("You don't have access to this list."))
            
            return list_obj
        except List.DoesNotExist:
            raise NotFound(_("List not found."))
    
    @swagger_auto_schema(responses={200: TaskListSerializer(many=True)})
    def get(self, request, list_id):
        """Return all tasks in the list"""
        list_obj = self.get_list_with_access_check(list_id, request.user)
        
        tasks = Task.objects.filter(list=list_obj).order_by('position', 'created_at')
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=TaskCreateSerializer,
        responses={201: TaskDetailSerializer, 400: _("Bad Request")}
    )
    def post(self, request, list_id):
        """Create a new task in the list"""
        list_obj = self.get_list_with_access_check(list_id, request.user)
        
        # Add list to request data
        data = request.data.copy()
        data['list'] = list_obj.id
        
        serializer = TaskCreateSerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            task = serializer.save()
            response_serializer = TaskDetailSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    """
    View for retrieving, updating or deleting a specific task.
    
    Behaviour:
    - GET: Return task details.
    - PATCH: Update task information (board members only).
    - DELETE: Delete the task (creator or board owner/admin only).
    - Access permissions are checked for every action.
    
    Endpoint: GET/PATCH/DELETE /api/v1/tasks/{pk}/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_task_with_access_check(self, pk, user):
        """Get task and verify user has access to it"""
        try:
            task = Task.objects.get(pk=pk)
            board = task.list.board
            
            # Check if user is board owner or member
            if board.owner != user:
                if not board.active_members.filter(user=user).exists():
                    raise PermissionDenied(_("You don't have access to this task."))
            
            return task
        except Task.DoesNotExist:
            raise NotFound(_("Task not found."))
    
    @swagger_auto_schema(responses={200: TaskDetailSerializer})
    def get(self, request, pk):
        """Return task details"""
        task = self.get_task_with_access_check(pk, request.user)
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=TaskUpdateSerializer, responses={200: TaskDetailSerializer, 400: _("Bad Request")})
    def patch(self, request, pk):
        """Update task information"""
        task = self.get_task_with_access_check(pk, request.user)
        
        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        
        if serializer.is_valid():
            task = serializer.save()
            response_serializer = TaskDetailSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(responses={204: _("No Content"), 403: _("Forbidden")})
    def delete(self, request, pk):
        """Delete task (creator or board owner/admin only)"""
        task = self.get_task_with_access_check(pk, request.user)
        user = request.user
        board = task.list.board
        
        # Check delete permission (creator, board owner, or admin)
        can_delete = False
        if task.created_by == user or board.owner == user:
            can_delete = True
        else:
            # Check if user is admin
            try:
                membership = BoardMembership.objects.get(
                    board=board, user=user, status='accepted'
                )
                if membership.role == 'admin':
                    can_delete = True
            except BoardMembership.DoesNotExist:
                pass
        
        if not can_delete:
            return Response(
                {"error": _("Only the task creator, board owner, or admin can delete this task.")},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task.delete()
        return Response(
            {"message": _("Task deleted successfully")},
            status=status.HTTP_204_NO_CONTENT
        )


class UserTasksView(APIView):
    """
    View for listing tasks assigned to the authenticated user.
    
    Behaviour:
    - GET: Return all tasks assigned to the current user.
    - Can filter by completion status, priority, due date.
    - Only shows tasks from boards user has access to.
    
    Endpoint: GET /api/v1/tasks/my-tasks/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: TaskListSerializer(many=True)})
    def get(self, request):
        """Return user's assigned tasks"""
        user = request.user
        
        # Get all boards user has access to
        user_boards = user.all_boards
        
        # Filter tasks assigned to user in accessible boards
        tasks = Task.objects.filter(
            assigned_to=user,
            list__board__in=user_boards
        ).order_by('-created_at')
        
        # Apply filters
        is_completed = request.query_params.get('is_completed')
        priority = request.query_params.get('priority')
        overdue_only = request.query_params.get('overdue_only')
        
        if is_completed is not None:
            tasks = tasks.filter(is_completed=is_completed.lower() == 'true')
        
        if priority:
            tasks = tasks.filter(priority=priority)
        
        if overdue_only and overdue_only.lower() == 'true':
            from django.utils import timezone
            tasks = tasks.filter(
                due_date__lt=timezone.now().date(),
                is_completed=False
            )
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskCommentsView(APIView):
    """
    View for listing and creating task comments.
    
    Behaviour:
    - GET: Return all comments for the task.
    - POST: Create a new comment on the task.
    - Only board members can access comments.
    
    Endpoint: GET/POST /api/v1/tasks/{task_id}/comments/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_task_with_access_check(self, task_id, user):
        """Get task and verify user has access to it"""
        try:
            task = Task.objects.get(id=task_id)
            board = task.list.board
            
            # Check if user is board owner or member
            if board.owner != user:
                if not board.active_members.filter(user=user).exists():
                    raise PermissionDenied(_("You don't have access to this task."))
            
            return task
        except Task.DoesNotExist:
            raise NotFound(_("Task not found."))
    
    @swagger_auto_schema(responses={200: TaskCommentSerializer(many=True)})
    def get(self, request, task_id):
        """Return all comments for the task"""
        task = self.get_task_with_access_check(task_id, request.user)
        
        comments = TaskComment.objects.filter(task=task).order_by('created_at')
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=TaskCommentSerializer,
        responses={201: TaskCommentSerializer, 400: _("Bad Request")}
    )
    def post(self, request, task_id):
        """Create a new comment on the task"""
        task = self.get_task_with_access_check(task_id, request.user)
        
        serializer = TaskCommentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            comment = serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskMoveView(APIView):
    """
    View for moving tasks between lists or positions.
    
    Behaviour:
    - POST: Move task to new list and/or position.
    - Only board members can move tasks.
    - Validates target list is in same board.
    
    Endpoint: POST /api/v1/tasks/{pk}/move/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Toggle result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'task': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: 'Forbidden',
            404: 'Not Found'
        }
    )
    def post(self, request, pk):
        """Move task to new list/position"""
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(
                {"error": _("Task not found.")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user = request.user
        board = task.list.board
        
        # Check access permission
        if board.owner != user:
            if not board.active_members.filter(user=user).exists():
                return Response(
                    {"error": _("You don't have access to this task.")},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = TaskMoveSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            new_list = serializer.validated_data.get('new_list')
            new_position = serializer.validated_data.get('new_position')
            
            try:
                if new_list and new_list != task.list:
                    # Moving to different list
                    if new_list.board != board:
                        return Response(
                            {"error": _("Cannot move task to a list in a different board.")},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    task.move_to_list(new_list, new_position)
                elif new_position:
                    # Moving within same list
                    task.move_to_position(new_position)
                
                response_serializer = TaskDetailSerializer(task)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
                
            except ValidationError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskToggleCompleteView(APIView):
    """
    View for toggling task completion status.
    
    Behaviour:
    - POST: Toggle task between completed and incomplete.
    - Only board members can toggle completion.
    - Provides a quick way to mark tasks as done/undone.
    
    Endpoint: POST /api/v1/tasks/{pk}/toggle-complete/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Toggle result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'task': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: 'Forbidden',
            404: 'Not Found'
        }
    )
    def post(self, request, pk):
        """Toggle task completion status"""
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(
                {"error": _("Task not found.")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user = request.user
        board = task.list.board
        
        # Check access permission
        if board.owner != user:
            if not board.active_members.filter(user=user).exists():
                return Response(
                    {"error": _("You don't have access to this task.")},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if task.is_completed:
            task.mark_incomplete()
            message = _("Task marked as incomplete")
        else:
            task.mark_completed()
            message = _("Task marked as completed")
        
        response_serializer = TaskDetailSerializer(task)
        return Response({
            "message": message,
            "task": response_serializer.data
        }, status=status.HTTP_200_OK)


class TaskCommentDetailView(APIView):
    """
    View for retrieving, updating or deleting a specific comment.
    
    Behaviour:
    - GET: Return comment details.
    - PATCH: Update comment content (author only).
    - DELETE: Delete the comment (author or board owner/admin only).
    
    Endpoint: GET/PATCH/DELETE /api/v1/comments/{pk}/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_comment_with_access_check(self, pk, user):
        """Get comment and verify user has access to it"""
        try:
            comment = TaskComment.objects.get(pk=pk)
            board = comment.task.list.board
            
            # Check if user is board owner or member
            if board.owner != user:
                if not board.active_members.filter(user=user).exists():
                    raise PermissionDenied(_("You don't have access to this comment."))
            
            return comment
        except TaskComment.DoesNotExist:
            raise NotFound(_("Comment not found."))
    
    @swagger_auto_schema(responses={200: TaskCommentSerializer})
    def get(self, request, pk):
        """Return comment details"""
        comment = self.get_comment_with_access_check(pk, request.user)
        serializer = TaskCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=TaskCommentUpdateSerializer, responses={200: TaskCommentSerializer, 400: _("Bad Request"), 403: _("Forbidden")})
    def patch(self, request, pk):
        """Update comment content (author only)"""
        comment = self.get_comment_with_access_check(pk, request.user)
        
        if comment.user != request.user:
            return Response(
                {"error": _("Only the comment author can edit this comment.")},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TaskCommentUpdateSerializer(comment, data=request.data, partial=True)
        
        if serializer.is_valid():
            comment = serializer.save()
            response_serializer = TaskCommentSerializer(comment)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(responses={204: _("No Content"), 403: _("Forbidden")})
    def delete(self, request, pk):
        """Delete comment (author or board owner/admin only)"""
        comment = self.get_comment_with_access_check(pk, request.user)
        user = request.user
        board = comment.task.list.board
        
        # Check delete permission (author, board owner, or admin)
        can_delete = False
        if comment.user == user or board.owner == user:
            can_delete = True
        else:
            # Check if user is admin
            try:
                membership = BoardMembership.objects.get(
                    board=board, user=user, status='accepted'
                )
                if membership.role == 'admin':
                    can_delete = True
            except BoardMembership.DoesNotExist:
                pass
        
        if not can_delete:
            return Response(
                {"error": _("Only the comment author, board owner, or admin can delete this comment.")},
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment.delete()
        return Response(
            {"message": _("Comment deleted successfully")},
            status=status.HTTP_204_NO_CONTENT
        )
