from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied, NotFound
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import List
from .serializers import (
    ListSerializer, ListDetailSerializer, ListCreateSerializer,
    ListUpdateSerializer, ListMoveSerializer
)


class ListListView(APIView):
    """
    View for listing lists in a specific board.
    
    Behaviour:
    - GET: Return all lists for a board where user has access.
    - POST: Create a new list in the board.
    - Lists are ordered by position.
    - Only available to authenticated users with board access.
    
    Endpoint: GET/POST /api/v1/boards/{board_id}/lists/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_board_and_check_permission(self, board_id, user):
        """Get board and check if user has access"""
        from boards.models import Board
        
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user is owner or member of the board
        if not (board.owner == user or board.memberships.filter(user=user, status='accepted').exists()):
            raise PermissionDenied(_("You don't have permission to access this board."))
        
        return board 
    

    def get_board_and_check_permission_admin(self, board_id, user):
        """Get board and check if user has access"""
        from boards.models import Board
        
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user is owner or admin member of the board
        if not (board.owner == user or board.memberships.filter(user=user, status='accepted', role='admin').exists()):
            raise PermissionDenied(_("You don't have permission to access this board."))
        
        return board 
    


    @swagger_auto_schema(operation_summary=_("List all lists in a board"), responses={200: ListSerializer(many=True)})
    def get(self, request, board_id):
        """List all lists in a board"""
        board = self.get_board_and_check_permission(board_id, request.user)
        lists = board.lists.all()
        
        serializer = ListSerializer(lists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(operation_summary=_("Create a new list in a board"), request_body=ListCreateSerializer, responses={201: ListDetailSerializer, 400: _("Validation Error")})
    def post(self, request, board_id):
        """Create a new list in a board"""
        board = self.get_board_and_check_permission_admin(board_id, request.user)
        
        data = request.data.copy()
        data['board'] = board.id
        
        serializer = ListCreateSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            list_obj = serializer.save()
            response_serializer = ListDetailSerializer(list_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_list_and_check_permission(self, pk, user):
        list_obj = get_object_or_404(List, id=pk)
        board = list_obj.board
        if not (board.owner == user or board.memberships.filter(user=user, status='accepted').exists()):
            raise PermissionDenied(_("You don't have permission to access this list."))
        return list_obj
    
    def get_list_and_check_permission_admin(self, pk, user):
        list_obj = get_object_or_404(List, id=pk)
        board = list_obj.board
        if not (board.owner == user or board.memberships.filter(user=user, status='accepted', role='admin').exists()):
            raise PermissionDenied(_("You don't have permission to access this list."))
        return list_obj
    
    @swagger_auto_schema(operation_summary=_("Retrieve a list"), responses={200: ListDetailSerializer})
    def get(self, request, pk):
        list_obj = self.get_list_and_check_permission(pk, request.user)
        serializer = ListDetailSerializer(list_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(operation_summary=_("Partially update a list"), request_body=ListUpdateSerializer, responses={200: ListDetailSerializer, 400: _("Validation Error")})
    def patch(self, request, pk):
        list_obj = self.get_list_and_check_permission_admin(pk, request.user)
        serializer = ListUpdateSerializer(list_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_summary=_("Delete a list"), responses={204: _("No Content")})
    def delete(self, request, pk):
        list_obj = self.get_list_and_check_permission_admin(pk, request.user)
        list_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListMoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_list_and_check_permission(self, pk, user):
        list_obj = get_object_or_404(List, id=pk)
        board = list_obj.board
        if not (board.owner == user or board.memberships.filter(user=user, status='accepted', role='admin').exists()):
            raise PermissionDenied(_("You don't have permission to move this list."))
        return list_obj
    
    @swagger_auto_schema(operation_summary=_("Move list to new position"), request_body=ListMoveSerializer, responses={200: ListDetailSerializer, 400: _("Validation Error")})
    def post(self, request, pk):
        list_obj = self.get_list_and_check_permission(pk, request.user)
        serializer = ListMoveSerializer(data=request.data)
        if serializer.is_valid():
            new_position = serializer.validated_data['position']
            list_obj.move_to_position(new_position)
            response_serializer = ListDetailSerializer(list_obj)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
