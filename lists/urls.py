
from django.urls import path
from . import views

app_name = 'lists'

urlpatterns = [
    # List detail operations
    # Retrieve, update, or delete a specific list
    path('<int:list_id>/', views.ListDetailView.as_view(), name='list-detail'),
    
    # Move a list to a new position within the same board
    path('<int:list_id>/move/', views.ListMoveView.as_view(), name='list-move'),
]
