from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import (
    RegisterView, UserListView, UserDetailView, 
    ChangePasswordView, ProfileView, current_user
)

urlpatterns = [
    # Authentication endpoints
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # User management endpoints
    path("users/", UserListView.as_view(), name="user_list"),  # GET: list all users (admin only)
    path("users/me/", UserDetailView.as_view(), name="current_user_detail"),  # GET/PATCH/: current user
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),  # GET/PATCH/: specific user
    path("users/current/", current_user, name="current_user"),  # GET: current user info
    
    # Password management
    path("users/change-password/", ChangePasswordView.as_view(), name="change_password"),
    
    # Profile management
    path("profiles/me/", ProfileView.as_view(), name="current_user_profile"),  # GET/PATCH: current user profile
    path("profiles/<int:pk>/", ProfileView.as_view(), name="user_profile"),  # GET/PATCH: specific user profile
]
