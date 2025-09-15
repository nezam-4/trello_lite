from django.urls import path
from boards.views import UserLimitsView

app_name = 'limits'

urlpatterns = [
    # User limits and quotas
    path("", UserLimitsView.as_view(), name="user_limits"),  # GET: current user's limits
    path("<int:user_id>/", UserLimitsView.as_view(), name="specific_user_limits"),  # GET: specific user's limits (admin only)
]
