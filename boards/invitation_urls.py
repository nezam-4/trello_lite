from django.urls import path
from boards.views import (
    UserInvitationListView,
    BoardInvitationRespondView,
)

app_name = 'invitations'

urlpatterns = [
    # Invitation management (user-centric)
    path("", UserInvitationListView.as_view(), name="invitation_list"),  # GET: list user's invitations
    path("<int:pk>/", BoardInvitationRespondView.as_view(), name="invitation_detail"),  # GET: invitation detail
    path("<int:pk>/respond/", BoardInvitationRespondView.as_view(), name="invitation_respond"),  # POST: accept/reject
]
