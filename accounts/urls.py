from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import (
    RegisterView, UserListView, UserDetailView, 
    ChangePasswordView, ProfileView, current_user, LogoutView,
    PasswordResetRequestView, PasswordResetConfirmView,
)

urlpatterns = [
    # Authentication endpoints
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    # Password reset flow
    path("auth/password/reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("auth/password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    
    # User management endpoints
    path("", UserListView.as_view(), name="user_list"),  # GET: list all users (admin only)
    path("me/", UserDetailView.as_view(), name="current_user_detail"),  # GET/PATCH/: current user
    path("<int:pk>/", UserDetailView.as_view(), name="user_detail"),  # GET/PATCH/: specific user
    path("current/", current_user, name="current_user"),  # GET: current user info
    
    # Password management
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    
    # Profile management
    path("profile/", ProfileView.as_view(), name="current_user_profile"),  # GET/PATCH: current user profile
    path("profile/<int:pk>/", ProfileView.as_view(), name="user_profile"),  # GET/PATCH: specific user profile
]
