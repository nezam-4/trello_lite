from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import (
    RegisterView, LogoutView,
    PasswordResetRequestView, PasswordResetConfirmView,
    EmailVerificationView,
)

app_name = 'auth'

urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # Password reset
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    
    # Email verification
    path("verify-email/", EmailVerificationView.as_view(), name="verify_email"),
]
