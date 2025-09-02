from django.urls import path
from .views import (
    TaskListView, TaskDetailView, TaskMoveView, TaskToggleCompleteView,
    UserTasksView, TaskCommentsView, TaskCommentDetailView
)

app_name = 'tasks'

urlpatterns = [
    # Task endpoints
    path('lists/<int:list_id>/tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/move/', TaskMoveView.as_view(), name='task-move'),
    path('tasks/<int:pk>/toggle-complete/', TaskToggleCompleteView.as_view(), name='task-toggle-complete'),
    
    # User tasks
    path('tasks/my-tasks/', UserTasksView.as_view(), name='user-tasks'),
    
    # Task comments endpoints
    path('tasks/<int:task_id>/comments/', TaskCommentsView.as_view(), name='task-comments'),
    path('comments/<int:pk>/', TaskCommentDetailView.as_view(), name='comment-detail'),
]
