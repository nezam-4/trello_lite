from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

from .models import Board, BoardMembership, BoardInvitation, BoardActivity
from .serializers import (
    BoardListSerializer, BoardDetailSerializer, BoardCreateSerializer, 
    BoardUpdateSerializer, BoardMembershipSerializer, BoardInvitationSerializer,
    BoardActivitySerializer
)
from .utils import (
    check_user_board_limit, check_board_member_limit, 
    check_user_membership_limit, get_user_limits_info
)

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
    
    def get(self, request):
        user = request.user
        # Use all_boards property to fetch all boards of the user
        boards = user.all_boards.order_by('-created_at')
        
        serializer = BoardListSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    """
    View for creating a new board.

    Behaviour:
    - POST: Create a new board from the provided payload.
    - Checks the user's board limit before creation.
    - Automatically sets the current user as the board owner.
    - Logs the creation activity.
    - Returns the full board details on success.

    Endpoint: POST /api/v1/boards/
    """
    def post(self, request):
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
    
    def get(self, request, pk):
        """Return full board details"""
        board = self.get_board(pk, request.user)
        serializer = BoardDetailSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
    
    def get(self, request):
        # Fetch all public boards
        boards = Board.objects.filter(is_public=True).order_by('-created_at')
        serializer = BoardListSerializer(boards, many=True)
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

    Behaviour:
    - POST: Create an invitation for a user (email delivery will be added later).
    - Only the board owner or admins can invite.
    - Checks member limits before inviting.
    - Generates a unique token for the invitation.
    - Logs the invite activity.

    Note: Email delivery of invitations will be implemented in future versions.
    Endpoint: POST /api/v1/boards/{board_id}/invite/
    """
    permission_classes = [permissions.IsAuthenticated]
    
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
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

