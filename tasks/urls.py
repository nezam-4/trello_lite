from django.urls import path
from .views import (
    TaskListView, TaskDetailView, TaskMoveView, TaskToggleCompleteView,
    UserTasksView, TaskCommentsView, TaskCommentDetailView
)

app_name = 'tasks'

urlpatterns = [
    # Task CRUD operations
    path('', UserTasksView.as_view(), name='user-tasks'),  # GET: list user's assigned tasks
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),  # GET/PATCH/DELETE: task detail
    
    # Task actions (as sub-resources)
    path('<int:pk>/move/', TaskMoveView.as_view(), name='task-move'),  # POST: move task
    path('<int:pk>/toggle-complete/', TaskToggleCompleteView.as_view(), name='task-toggle-complete'),  # POST: toggle completion
    
    # Task comments (nested resource)
    path('<int:task_id>/comments/', TaskCommentsView.as_view(), name='task-comments'),  # GET: list, POST: create
    path('<int:task_id>/comments/<int:pk>/', TaskCommentDetailView.as_view(), name='comment-detail'),  # GET/PATCH/DELETE
    
    # Board-specific task operations (should be in boards app but kept for compatibility)
    path('lists/<int:list_id>/', TaskListView.as_view(), name='list-tasks'),  # GET: list, POST: create
]
