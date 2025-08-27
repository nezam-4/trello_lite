from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes

from .models import CustomUser, Profile
from .serilizer import (
    RegisterSerializer, UserSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, ProfileSerializer
)


class RegisterView(APIView):
    """User registration endpoint that returns JWT tokens"""
    permission_classes = [AllowAny]
    serializer_class=RegisterSerializer
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
        
        profile = self.get_object(user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

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
        
        profile = self.get_object(user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user details"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
