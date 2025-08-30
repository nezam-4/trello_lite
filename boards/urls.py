from django.urls import path
from . import views

app_name = 'boards'

urlpatterns = [
    # Main CRUD operations for boards
    # List all boards of the user (owner or member)
    # Create a new board while checking user limits
    path('', views.BoardListView.as_view(), name='board-list'),
    
    # Retrieve, update, or delete a specific board
    path('<int:pk>/', views.BoardDetailView.as_view(), name='board-detail'),
    
    # List public boards to discover new ones
    path('public/', views.PublicBoardListView.as_view(), name='public-boards'),
    
    # Board members management
    # List members of a specific board
    path('<int:board_id>/members/', views.BoardMembersView.as_view(), name='board-members'),
    
    # Invite a new user to the board via email
    path('<int:board_id>/invite/', views.BoardInviteView.as_view(), name='board-invite'),
    
    # Leave a board as a member (owner cannot leave)
    path('<int:board_id>/leave/', views.BoardLeaveView.as_view(), name='board-leave'),
    
    # Join a board via invitation link
    path('join/<str:token>/', views.BoardJoinView.as_view(), name='board-join'),
    
    # Show activity history of a board
    path('<int:board_id>/activities/', views.BoardActivitiesView.as_view(), name='board-activities'),
    
    # Show current user limits (number of boards, memberships)
    path('limits/', views.UserLimitsView.as_view(), name='user-limits'),
]
