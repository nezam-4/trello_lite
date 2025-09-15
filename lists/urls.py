from django.urls import path
from . import views

app_name = 'lists'

urlpatterns = [
    # List detail operations
    # Retrieve, update, or delete a specific list
    path('<int:pk>/', views.ListDetailView.as_view(), name='list-detail'),
    
    # Move a list to a new position within the same board
    path('<int:pk>/move/', views.ListMoveView.as_view(), name='list-move'),
]
