from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import CustomUser, Profile
from .serilizer import (
    RegisterSerializer, UserSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, ProfileSerializer
)

class RegisterView(APIView):
    """User registration endpoint that returns JWT tokens"""
    permission_classes = [AllowAny]
    serializer_class=RegisterSerializer
    @swagger_auto_schema(
        operation_summary=_('Register a new user'), 
        request_body=RegisterSerializer, 
        responses={201: UserSerializer, 400: _('Validation Error')}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": _("User registered successfully"),
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    """List all users - Admin only"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary=_('List all users (Admin only)'), 
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request):
        # Only allow staff/admin to view all users
        if not request.user.is_staff:
            return Response(
                {"detail": _("You do not have permission to perform this action.")},
                status=status.HTTP_403_FORBIDDEN
            )
        
        users = CustomUser.objects.all().select_related('profile')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    """Retrieve, update user details"""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(CustomUser, pk=pk)

    @swagger_auto_schema(
        operation_summary=_('Retrieve a user detail'), 
        responses={200: UserSerializer}
    )
    def get(self, request, pk=None):
        # If no pk provided, return current user
        if pk is None:
            user = request.user
        else:
            user = self.get_object(pk)
            # Users can only view their own profile unless they're staff
            if user != request.user and not request.user.is_staff:
                return Response(
                    {"detail": _("You do not have permission to view this user.")},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary=_('Partially update a user'), 
        request_body=UserUpdateSerializer, 
        responses={200: UserSerializer, 400: _('Validation Error')}
    )
    def patch(self, request, pk=None):
        # If no pk provided, update current user
        if pk is None:
            user = request.user
        else:
            user = self.get_object(pk)
            # Users can only update their own profile
            if user != request.user:
                return Response(
                    {"detail": _("You do not have permission to update this user.")},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data,status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ChangePasswordView(APIView):
    """Change user password"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary=_('Change current user\'s password'), 
        request_body=ChangePasswordSerializer, 
        responses={200: _('Password changed'), 400: _('Validation Error')}
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": _("Password changed successfully")},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """Retrieve and update user profile"""
    permission_classes = [IsAuthenticated]

    def get_object(self, user):
        profile, created = Profile.objects.get_or_create(user=user)
        return profile

    @swagger_auto_schema(
        operation_summary=_('Retrieve a user\'s profile'), 
        responses={200: ProfileSerializer}
    )
    def get(self, request, pk=None):
        if pk is None:
            user = request.user
        else:
            user = get_object_or_404(CustomUser, pk=pk)
            # Users can only view their own profile unless they're staff
            if user != request.user and not request.user.is_staff:
                return Response(
                    {"detail": _("You do not have permission to view this profile.")},
                    status=status.HTTP_403_FORBIDDEN
                )
        u_serializer=UserUpdateSerializer(user)
        profile = self.get_object(user)
        p_serializer = ProfileSerializer(profile)
        return Response({"user": u_serializer.data, "profile": p_serializer.data})

    @swagger_auto_schema(
        operation_summary=_('Partially update a profile'), 
        request_body=ProfileSerializer, 
        responses={200: ProfileSerializer, 400: _('Validation Error')}
    )
    def patch(self, request, pk=None):
        if pk is None:
            user = request.user
        else:
            user = get_object_or_404(CustomUser, pk=pk)
            # Users can only update their own profile
            if user != request.user:
                return Response(
                    {"detail": _("You do not have permission to update this profile.")},
                    status=status.HTTP_403_FORBIDDEN
                )
        u_serializer=UserUpdateSerializer(user, data=request.data, partial=True)
        if u_serializer.is_valid():
            u_serializer.save()
        profile = self.get_object(user)
        p_serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if p_serializer.is_valid():
            p_serializer.save()
            return Response({"user": u_serializer.data, "profile": p_serializer.data}, status=status.HTTP_200_OK)
        return Response({"user": u_serializer.errors, "profile": p_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@swagger_auto_schema(
    operation_summary=_('Get current authenticated user'), 
    responses={200: UserSerializer}
)
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user details"""
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)
