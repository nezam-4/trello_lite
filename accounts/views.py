from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from urllib.parse import urlencode
from django.conf import settings
from django.urls import reverse     
from .models import CustomUser, Profile
from .serializers import (
    RegisterSerializer, UserSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, ProfileSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
)
from .tasks import send_password_reset_email, send_email_verification

class RegisterView(APIView):
    """User registration endpoint that sends an email verification link"""
    permission_classes = [AllowAny]
    serializer_class=RegisterSerializer
    @swagger_auto_schema(
        operation_summary=_('Register a new user'), 
        request_body=RegisterSerializer, 
        responses={201: openapi.Response(description=_('Registration successful, please verify your email')), 400: _('Validation Error')}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Ensure user is inactive until email is verified
            if user.is_active:
                user.is_active = False
                user.save(update_fields=['is_active'])

            # Generate verification token and send email
            token = user.generate_verification_token()
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build verification link: prefer frontend route if configured
            query_params = urlencode({'uid': uid, 'token': token})
            frontend_url = getattr(settings, 'FRONTEND_URL', None)
            if frontend_url:
                # Point email link to frontend verification page
                verification_link = f"{frontend_url.rstrip('/')}/verify-email?{query_params}"
            else:
                # Fallback to backend API endpoint
                try:
                    verification_base = reverse('accounts:verify_email')
                except Exception:
                    try:
                        verification_base = reverse('verify_email')
                    except Exception:
                        verification_base = '/api/v1/users/auth/verify-email/'
                verification_link = f"{settings.SITE_URL.rstrip('/')}{verification_base}?{query_params}"
            
            send_email_verification.delay(user.id, verification_link)
            return Response({
                "message": _("Registration successful. Please check your email to verify your account."),
                "user": UserSerializer(user).data,
                "email_verification_sent": True
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """Verify user's email and activate account"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary=_('Verify email address'),
        manual_parameters=[
            openapi.Parameter('uid', openapi.IN_QUERY, description=_('User ID (base64)'), type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('token', openapi.IN_QUERY, description=_('Verification token'), type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: openapi.Response(description=_('Email verified successfully')), 400: openapi.Response(description=_('Invalid or expired token'))}
    )
    def get(self, request):
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')
        if not uidb64 or not token:
            return Response({"detail": _("Missing parameters")}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from django.utils.http import urlsafe_base64_decode
            from django.utils.encoding import force_str
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except Exception:
            return Response({"detail": _("Invalid verification link.")}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_verification_token_valid(token):
            user.verify_email()
            return Response({"message": _("Email verified successfully. You can now log in.")}, status=status.HTTP_200_OK)
        return Response({"detail": _("Invalid or expired verification token.")}, status=status.HTTP_400_BAD_REQUEST)


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
        # Validate both user and profile updates; if either has errors, return 400
        profile = self.get_object(user)
        u_serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        p_serializer = ProfileSerializer(profile, data=request.data, partial=True)
        u_valid = u_serializer.is_valid()
        p_valid = p_serializer.is_valid()
        if not u_valid or not p_valid:
            return Response({"user": u_serializer.errors, "profile": p_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        # Both serializers are valid; save and return updated representations
        u_serializer.save()
        p_serializer.save()
        return Response({"user": u_serializer.data, "profile": p_serializer.data}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Logout user by blacklisting refresh token"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary=_('Logout user and blacklist refresh token'),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description=_('Refresh token to blacklist'))
            },
            required=['refresh_token']
        ),
        responses={
            200: openapi.Response(description=_('Successfully logged out')),
            400: openapi.Response(description=_('Invalid token'))
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"detail": _("Refresh token is required")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": _("Successfully logged out")},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": _("Invalid token")},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetRequestView(APIView):
    """Request a password reset by email"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary=_('Request password reset'),
        request_body=PasswordResetRequestSerializer,
        responses={200: openapi.Response(description=_('Email sent if account exists'))}
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        try:
            # Allow password reset for inactive users as well (used to re-activate accounts)
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # Build frontend reset link and send via Celery
            reset_base = reverse('accounts:password_reset_confirm')
            frontend_url = getattr(settings, 'FRONTEND_URL', None)

            if frontend_url:
                # Point email link to frontend reset page (SPA route)
                reset_base = f"{frontend_url.rstrip('/')}/reset-password"
            else:
                # Fallback to backend API endpoint
                reset_base = f"{settings.SITE_URL.rstrip('/')}{reset_base}"
            query_params = urlencode({'uid': uid, 'token': token})
            reset_link = f"{reset_base}?{query_params}"

            send_password_reset_email.delay(user.id, reset_link)
        except CustomUser.DoesNotExist:
            # Intentionally do not reveal whether email exists
            pass

        return Response({
            "message": _("If an account with that email exists, we've sent a password reset link.")
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """Confirm a password reset and set a new password"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary=_('Confirm password reset'),
        request_body=PasswordResetConfirmSerializer,
        responses={200: openapi.Response(description=_('Password reset successful')), 400: openapi.Response(description=_('Validation error'))}
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": _("Password has been reset successfully.")}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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
