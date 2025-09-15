from django.urls import path
from accounts.views import (
    UserListView, UserDetailView, 
    ChangePasswordView, current_user
)

app_name = 'users'

urlpatterns = [
    # User management
    path("", UserListView.as_view(), name="user_list"),  # GET: list all users (admin only)
    path("me/", UserDetailView.as_view(), name="current_user_detail"),  # GET/PATCH/DELETE: current user
    path("current/", current_user, name="current_user"),  # GET: current user info (deprecated, use me/)
    path("<int:pk>/", UserDetailView.as_view(), name="user_detail"),  # GET/PATCH/DELETE: specific user
    
    # Nested resource for password
    path("<int:pk>/password/", ChangePasswordView.as_view(), name="change_password"),
    path("me/password/", ChangePasswordView.as_view(), name="current_user_change_password"),
]
