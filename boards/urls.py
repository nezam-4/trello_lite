from django.urls import path
from . import views

app_name = 'boards'

urlpatterns = [
    # Board CRUD operations
    path('', views.BoardListView.as_view(), name='board-list'),  # GET: list, POST: create
    path('<int:pk>/', views.BoardDetailView.as_view(), name='board-detail'),  # GET/PATCH/DELETE
    
    # Public boards discovery
    path('public/', views.PublicBoardListView.as_view(), name='public-boards'),  # GET: list public boards
    
    # Board members (nested resource)
    path('<int:board_id>/members/', views.BoardMembersView.as_view(), name='board-members'),  # GET: list members
    path('<int:board_id>/members/<int:user_id>/', views.BoardRemoveMemberView.as_view(), name='board-member-detail'),  # DELETE: remove member
    
    # Board invitations (nested resource)
    path('<int:board_id>/invitations/', views.BoardInviteView.as_view(), name='board-invitations'),  # GET: list, POST: create
    path('<int:board_id>/invitations/user/', views.BoardUserInviteView.as_view(), name='board-invite-user'),  # POST: invite registered user
    
    # Board actions
    path('<int:board_id>/leave/', views.BoardLeaveView.as_view(), name='board-leave'),  # POST: leave board
    
    # Board activity log
    path('<int:board_id>/activities/', views.BoardActivitiesView.as_view(), name='board-activities'),  # GET: activity history
    
    # Board lists (nested resource)
    path('<int:board_id>/lists/', views.BoardListsView.as_view(), name='board-lists'),  # GET: list, POST: create
]
