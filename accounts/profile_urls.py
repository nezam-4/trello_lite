from django.urls import path
from accounts.views import ProfileView

app_name = 'profiles'

urlpatterns = [
    # Profile management
    path("", ProfileView.as_view(), name="profile_list"),  # GET: list all profiles (if needed)
    path("me/", ProfileView.as_view(), name="current_profile"),  # GET/PATCH: current user profile
    path("<int:pk>/", ProfileView.as_view(), name="profile_detail"),  # GET/PATCH: specific user profile
]
