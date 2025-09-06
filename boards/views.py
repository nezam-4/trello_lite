from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

from .models import Board, BoardMembership, BoardInvitation, BoardActivity
from .serializers import (
    BoardListSerializer, BoardDetailSerializer, BoardCreateSerializer, 
    BoardUpdateSerializer, BoardMembershipSerializer, BoardInvitationSerializer,
    BoardActivitySerializer, BoardUserInvitationSerializer
)
from .utils import (
    check_user_board_limit, check_board_member_limit, 
    check_user_membership_limit, get_user_limits_info
)
from .tasks import send_board_invitation_email, send_registered_invitation_email
from django.db.models import Q

User = get_user_model()


class BoardListView(APIView):
    """
    View for listing all boards the authenticated user owns or is a member of.

    Behaviour:
    - GET: Return every board where the user is the owner or a member.
    - Uses the `all_boards` property of `CustomUser` to fetch accessible boards.
    - Boards are ordered by creation date (newest first).
    - Only available to authenticated users.

    Endpoint:  GET /api/v1/boards/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: BoardListSerializer(many=True)})
    def get(self, request):
        user = request.user
        # Use all_boards property to fetch all boards of the user
        boards = user.all_boards.order_by('-created_at')
        
        serializer = BoardListSerializer(boards, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(request_body=BoardCreateSerializer, responses={201: BoardDetailSerializer, 400: 'Bad Request'})
    def post(self, request):
        """
        Create a new board.

        - Validates input via `BoardCreateSerializer`.
        - Enforces the user's board-creation limit.
        - Sets the current user as owner.
        - Logs creation activity.
        - Returns full board details on success.
        """
        serializer = BoardCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Check the user's board limit
            user = request.user
            can_create, remaining = check_user_board_limit(user)
            
            if not can_create:
                return Response(
                    {"error": _("You have reached the maximum number of boards allowed.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create board with current user set as owner
            board = serializer.save() # user is set in serializer
            
            # Log activity
            BoardActivity.objects.create(
                board=board,
                action='create',
                user=user,
                description=f"Board '{board.title}' created"
            )
            
            # Return full board information
            response_serializer = BoardDetailSerializer(board)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BoardDetailView(APIView):
    """
    View for retrieving, updating or deleting a specific board.

    Behaviour:
    - GET    : Return board details.
    - PATCH  : Update board information (owner or admin only).
    - DELETE : Delete the board (owner only).
    - Access permissions are checked for every action.
    - All changes are logged in `BoardActivity`.

    Endpoint: GET/PATCH/DELETE /api/v1/boards/{pk}/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_board(self, pk, user):
        """
        Retrieve board while validating user access
        - Uses all_boards property for access validation
        - Raises 404 if access is denied
        """
        try:
            board = user.all_boards.get(pk=pk)
            return board
        except Board.DoesNotExist:
            raise NotFound(_("Board not found or you do not have access."))
    
    @swagger_auto_schema(responses={200: BoardDetailSerializer})
    def get(self, request, pk):
        """Return full board details"""
        board = self.get_board(pk, request.user)
        serializer = BoardDetailSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=BoardUpdateSerializer, responses={200: BoardDetailSerializer, 400: 'Bad Request', 403: 'Forbidden'})
    def patch(self, request, pk):
        """
        Edit board information
        - Only owner or admin members can edit
        - Logs update activity
        """
        board = self.get_board(pk, request.user)
        user = request.user
        
        # Verify edit permission (owner or admin)
        if board.owner != user:
            try:
                membership = BoardMembership.objects.get(
                    board=board, user=user, status='accepted'
                )
                if membership.role != 'admin':
                    return Response(
                        {"error": _("Only the board owner or an admin can edit the board.")},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except BoardMembership.DoesNotExist:
                return Response(
                    {"error": _("You do not have permission to edit this board.")},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = BoardUpdateSerializer(board, data=request.data, partial=True)
        
        if serializer.is_valid():
            board = serializer.save()
            
            # Log edit activity
            BoardActivity.objects.create(
                board=board,
                action='update',
                user=user,
                description=f"Board '{board.title}' updated"
            )
            
            response_serializer = BoardDetailSerializer(board)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(responses={204: 'No Content', 403: 'Forbidden'})
    def delete(self, request, pk):
        """
        Delete board
        - Only the board owner can delete
        - Logs delete activity before removal
        """
        board = self.get_board(pk, request.user)
        user = request.user
        
        # Only the owner can delete the board
        if board.owner != user:
            return Response(
                {"error": _("Only the board owner can delete the board.")},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Log the deletion before deleting
        BoardActivity.objects.create(
            board=board,
            action='delete',
            user=user,
            description=f"Board '{board.title}' deleted"
        )
        
        board.delete()
        return Response(
            {"message": _("Board deleted successfully")},
            status=status.HTTP_204_NO_CONTENT
        )


class PublicBoardListView(APIView):
    """
    View for listing public boards.

    Behaviour:
    - GET: Return all boards marked as public.
    - Accessible to any authenticated user.
    - Useful for board discovery.

    Endpoint: GET /api/v1/boards/public/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: BoardListSerializer(many=True)})
    def get(self, request):
        # Fetch all public boards
        boards = Board.objects.filter(is_public=True).order_by('-created_at')
        serializer = BoardListSerializer(boards, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class BoardMembersView(APIView):
    """
    View for listing members of a board.

    Behaviour:
    - GET: Return all active members of the board.
    - Only board members can access this list.
    - Includes each member's role and join date.

    Endpoint: GET /api/v1/boards/{board_id}/members/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: BoardMembershipSerializer(many=True), 403: 'Forbidden', 404: 'Not Found'})
    def get(self, request, board_id):
        # Check user access to board
        user = request.user
        try:
            board = user.all_boards.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {"error": _("Board not found or you do not have access.")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Fetch active board members
        memberships = BoardMembership.objects.filter(
            board=board, status='accepted'
        ).order_by('-created_at')
        
        serializer = BoardMembershipSerializer(memberships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BoardInviteView(APIView):
    """
    View for inviting users to a board.
    Post
    Behaviour:
    - POST: Create an invitation for a email.
    - Only the board owner or admins can invite.
    - Checks board member limit before inviting.
    - Generates a unique token for the invitation.
    - Logs the invite activity.
    Endpoint: POST /api/v1/boards/{board_id}/invite/

    Get
    Behaviour:
    - GET: Return all invitations for the board.
    - Only the board owner or admins can view.
    - Logs the invite activity.
    Endpoint: GET /api/v1/boards/{board_id}/invite/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: BoardInvitationSerializer(many=True), 403: 'Forbidden', 404: 'Not Found'})
    def get(self, request, board_id):
        user = request.user
        try:
            board = Board.objects.get(id=board_id)
            # Allow access for board owner or admin members
            if board.owner != user:
                try:
                    membership = BoardMembership.objects.get(
                        board=board, user=user, status='accepted'
                    )
                    if membership.role != 'admin':
                        return Response(
                            {"error": _("Only the board owner or an admin can view invitations.")},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except BoardMembership.DoesNotExist:
                    return Response(
                        {"error": _("You do not have permission to view invitations.")},
                        status=status.HTTP_403_FORBIDDEN
                    )
            invitation = BoardInvitation.objects.filter(board=board)
            invitations=BoardInvitationSerializer(invitation, many=True)

            return Response(invitations.data, status=status.HTTP_200_OK)
        except Board.DoesNotExist:
            return Response(
                {"error": _("Board not found or you do not have access.")},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        request_body=BoardInvitationSerializer,
        responses={
            201: BoardInvitationSerializer,
            400: 'Bad Request',
            403: 'Forbidden',
            404: 'Not Found',
        }
    )      
    def post(self, request, board_id):
        user = request.user
        
        # Verify board existence and user access
        try:
            board = user.all_boards.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {"error": _("Board not found or you do not have access.")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify invite permission (owner or admin)
        if board.owner != user:
            try:
                membership = BoardMembership.objects.get(
                    board=board, user=user, status='accepted'
                )
                if membership.role != 'admin':
                    return Response(
                        {"error": _("Only the board owner or an admin can invite a new member.")},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except BoardMembership.DoesNotExist:
                return Response(
                    {"error": _("You do not have permission to invite a new member.")},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = BoardInvitationSerializer(
            data=request.data,
            context={'request': request, 'board': board}
        )
        
        if serializer.is_valid():
            # Create invitation first so we have access to the saved instance
            invitation = serializer.save()

            # Log invitation activity (email)
            invited_identity = invitation.invited_email
            BoardActivity.objects.create(
                board=board,
                action='join',
                user=user,
                description=f"{invited_identity} has been invited to the board"
            )
            # send email with celery
            send_board_invitation_email.delay(invitation.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class BoardUserInviteView(APIView):
    """
    Invite an *already registered* user to a board using their username or email.

    POST /api/v1/boards/<board_id>/invite/user/
    Body: {"identifier": "username_or_email", "role": "member|admin"}
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=BoardUserInvitationSerializer,
        responses={
            201: BoardInvitationSerializer,
            400: 'Bad Request',
            403: 'Forbidden',
            404: 'Not Found',
        }
    )
    def post(self, request, board_id):
        user = request.user

        # Verify board existence and user access
        try:
            board = user.all_boards.get(id=board_id)
        except Board.DoesNotExist:
            return Response({"error": _("Board not found or you do not have access.")}, status=status.HTTP_404_NOT_FOUND)

        # Verify permission to invite (owner or admin)
        if board.owner != user:
            try:
                membership = BoardMembership.objects.get(board=board, user=user, status='accepted')
                if membership.role != 'admin':
                    return Response({"error": _("Only the board owner or an admin can invite a new member.")}, status=status.HTTP_403_FORBIDDEN)
            except BoardMembership.DoesNotExist:
                return Response({"error": _("You do not have permission to invite a new member.")}, status=status.HTTP_403_FORBIDDEN)

        serializer = BoardUserInvitationSerializer(data=request.data, context={'board': board})
        if serializer.is_valid():
            target_user = serializer.validated_data['target_user']
            role = serializer.validated_data.get('role', 'member')

            # Remove old processed invitations for this user/email on this board
            BoardInvitation.objects.filter(board=board, invited_email=target_user.email, is_used=True).delete()

            invitation = BoardInvitation.objects.create(
                board=board,
                user=target_user,
                invited_by=user,
                invited_email=target_user.email,
                role=role
            )

            # Log activity
            BoardActivity.objects.create(
                board=board,
                action='join',
                user=user,
                description=f"{target_user.username} has been invited to the board"
            )

            # Send notification email to registered user
            send_registered_invitation_email.delay(invitation.id)

            response_serializer = BoardInvitationSerializer(invitation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardLeaveView(APIView):
    """
    View for leaving a board.

    Behaviour:
    - POST: Remove the authenticated user from the board.
    - The board owner cannot leave their own board.
    - Deletes the user's membership.
    - Logs the leave activity.

    Endpoint: POST /api/v1/boards/{board_id}/leave/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(request_body=None, responses={200: 'Left the board', 400: 'Bad Request', 404: 'Not Found'})
    def post(self, request, board_id):
        user = request.user
        
        # Verify board existence and user access
        try:
            board = user.all_boards.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {"error": _("Board not found or you do not have access.")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # The board owner cannot leave their own board
        if board.owner == user:
            return Response(
                {"error": _("The board owner cannot leave their own board.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check user's membership
        try:
            membership = BoardMembership.objects.get(
                board=board, user=user, status='accepted'
            )
        except BoardMembership.DoesNotExist:
            return Response(
                {"error": _("You are not a member of this board.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete membership
        membership.delete()
        
        # Log leave activity
        BoardActivity.objects.create(
            board=board,
            action='leave',
            user=user,
            description=f"{user.username} left the board"
        )
        
        return Response(
            {"message": _("Left the board successfully")}, 
            status=status.HTTP_200_OK
        )


class BoardActivitiesView(APIView):
    """
    View for listing board activities.

    Behaviour:
    - GET: Return the complete activity history of the board.
    - Accessible only to board members.
    - Activities are ordered by date (newest first).
    - Includes activity type, acting user and description.

    Endpoint: GET /api/v1/boards/{board_id}/activities/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: BoardActivitySerializer(many=True), 404: 'Not Found'})
    def get(self, request, board_id):
        user = request.user
        
        # Verify board existence and user access
        try:
            board = user.all_boards.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {"error": _("Board not found or you do not have access.")},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Fetch board activities
        activities = BoardActivity.objects.filter(board=board).order_by('-created_at')
        serializer = BoardActivitySerializer(activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserInvitationListView(APIView):
    """
    List all board invitations related to the authenticated user.

    GET /api/v1/boards/invitations/
    - Invitations where invited_email == user.email OR user == current user.
    - Only not expired or unused invitations can be filtered here (current behaviour filters is_used=False).
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: BoardListSerializer(many=True)})
    def get(self, request):
        user = request.user
        invitations = BoardInvitation.objects.filter(
            Q(invited_email=user.email) | Q(user=user)
        ).order_by('-created_at').filter(is_used=False)
        serializer = BoardInvitationSerializer(invitations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BoardInvitationRespondView(APIView):
    """Handle accept or reject of a board invitation.

    POST /api/v1/boards/invitations/<int:pk>/respond/
    Body: {"action": "accept" | "reject"}
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'action': openapi.Schema(type=openapi.TYPE_STRING, enum=['accept','reject'])},
        required=['action']
    ), responses={200: 'Success', 400: 'Bad Request', 404: 'Not Found', 403: 'Forbidden'})
   
    def post(self, request, pk):
        action = request.data.get('action')
        if action not in ('accept', 'reject'):
            return Response({"error": _("Action must be 'accept' or 'reject'.")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = BoardInvitation.objects.get(pk=pk, is_used=False)
        except BoardInvitation.DoesNotExist:
            return Response({"error": _("Invitation not found or already processed.")}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if not (invitation.user == user or invitation.invited_email == user.email):
            return Response({"error": _("This invitation is not for you." )}, status=status.HTTP_403_FORBIDDEN)

        if invitation.is_expired:
            return Response({"error": _("Invitation has expired.")}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'reject':
            invitation.is_used = True
            invitation.save()
            BoardActivity.objects.create(
                board=invitation.board,
                action='leave',  # treat as declined
                user=user,
                description=f"{user.username} rejected the invitation"
            )
            return Response({"message": _("Invitation rejected.")}, status=status.HTTP_200_OK)

        # action == 'accept'
        can_add_member, _remaining_slots = check_board_member_limit(invitation.board)
        can_join, _remaining_memberships = check_user_membership_limit(user)
        if not can_add_member:
            return Response({"error": _("Board has reached the maximum number of members.")}, status=status.HTTP_400_BAD_REQUEST)
        if not can_join:
            return Response({"error": _("You have reached the maximum number of board memberships.")}, status=status.HTTP_400_BAD_REQUEST)

        membership, created = BoardMembership.objects.get_or_create(
            board=invitation.board,
            user=user,
            defaults={
                'role': invitation.role,
                'status': 'accepted',
                'invited_by': invitation.invited_by,
                'response_at': timezone.now()
            }
        )
        if not created:
            return Response({"error": _("You are already a member of this board.")}, status=status.HTTP_400_BAD_REQUEST)

        invitation.is_used = True
        invitation.user = user
        invitation.save()

        BoardActivity.objects.create(
            board=invitation.board,
            action='join',
            user=user,
            description=f"{user.username} accepted the invitation"
        )

        return Response({"message": _("Successfully joined the board.")}, status=status.HTTP_200_OK)


class UserLimitsView(APIView):
    """
    View for displaying user limits.

    Behaviour:
    - GET: Return the current limits information of the user.
    - Includes number of boards created vs maximum allowed.
    - Includes number of memberships vs maximum allowed.
    - Intended for showing status in the dashboard.

    Endpoint: GET /api/v1/boards/limits/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: openapi.Response(description='User limits')})
    def get(self, request):
        user = request.user
        # Retrieve limit information via utils
        limits_info = get_user_limits_info(user)
        return Response(limits_info, status=status.HTTP_200_OK)


class BoardListsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: openapi.Response(description='List data')})
    def get(self, request, board_id):
        from lists.views import ListListView
        view = ListListView()
        return view.get(request, board_id)
    
    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT), responses={201: openapi.Response(description='Created list'), 400: 'Bad Request'})
    def post(self, request, board_id):
        from lists.views import ListListView
        view = ListListView()
        return view.post(request, board_id)
