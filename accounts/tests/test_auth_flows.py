from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from accounts.models import Profile

User = get_user_model()


class AuthenticationFlowTests(APITestCase):
    """Core authentication flow tests"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_user_registration_creates_inactive_user(self):
        """Registration: user should be created inactive and require email verification"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        
        response = self.client.post('/api/v1/auth/register/', data)
        
        # Check response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check user creation
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_email_verified)
        self.assertEqual(user.email, 'newuser@example.com')
        
        # Check profile creation
        self.assertTrue(hasattr(user, 'profile'))
        
    def test_email_verification_activates_user(self):
        """Email verification: user becomes active and verified"""
        # Create an inactive user
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            is_active=False
        )
        
        # Generate token and uid
        token = user.generate_verification_token()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Request email verification
        response = self.client.get(f'/api/v1/auth/verify-email/?uid={uid}&token={token}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Ensure user is activated
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_email_verified)
        
    def test_unverified_user_cannot_login(self):
        """Login: unverified user cannot log in"""
        # Create an inactive user
        User.objects.create_user(
            email='inactive@example.com',
            username='inactiveuser',
            password='TestPass123!',
            is_active=False
        )
        
        data = {
            'email': 'inactive@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post('/api/v1/auth/login/', data)
        
        # Inactive user should not obtain a token
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_verified_user_can_login(self):
        """Login: verified user can log in and receive tokens"""
        # Create an active user
        user = User.objects.create_user(
            email='active@example.com',
            username='activeuser',
            password='TestPass123!',
            is_active=True
        )
        # Mark email as verified by setting email_verified_at
        user.email_verified_at = timezone.now()
        user.save()
        
        data = {
            'email': 'active@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post('/api/v1/auth/login/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_token_refresh_works(self):
        """Token refresh should work"""
        # Create user and obtain tokens
        user = User.objects.create_user(
            email='refresh@example.com',
            username='refreshuser',
            password='TestPass123!',
            is_active=True
        )
        
        # Obtain initial token
        login_response = self.client.post('/api/v1/auth/login/', {
            'email': 'refresh@example.com',
            'password': 'TestPass123!'
        })
        
        refresh_token = login_response.data['refresh']
        
        # Refresh the token
        response = self.client.post('/api/v1/auth/refresh/', {
            'refresh': refresh_token
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
    def test_change_password_with_correct_old_password(self):
        """Change password with correct current password"""
        user = User.objects.create_user(
            email='change@example.com',
            username='changeuser',
            password='OldPass123!',
            is_active=True
        )
        
        self.client.force_authenticate(user=user)
        
        data = {
            'old_password': 'OldPass123!',
            'new_password1': 'NewPass123!',
            'new_password2': 'NewPass123!'
        }
        
        response = self.client.post('/api/v1/users/me/password/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password changed
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewPass123!'))
        
    def test_change_password_with_wrong_old_password(self):
        """Change password with incorrect current password should fail"""
        user = User.objects.create_user(
            email='wrong@example.com',
            username='wronguser',
            password='CorrectPass123!',
            is_active=True
        )
        
        self.client.force_authenticate(user=user)
        
        data = {
            'old_password': 'WrongPass123!',
            'new_password1': 'NewPass123!',
            'new_password2': 'NewPass123!'
        }
        
        response = self.client.post('/api/v1/users/me/password/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_profile_update_with_duplicate_username_fails(self):
        """Profile update: duplicate username should error and nothing should be saved"""
        # Create two users
        user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='Pass123!',
            is_active=True
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='Pass123!',
            is_active=True
        )
        
        self.client.force_authenticate(user=user2)
        
        # Attempt to change username to user1 (duplicate)
        data = {
            'username': 'user1',  # duplicate
            'bio': 'New bio text'
        }
        
        response = self.client.patch('/api/v1/profiles/me/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Ensure no changes in the database
        user2.refresh_from_db()
        self.assertEqual(user2.username, 'user2')  # username did not change
        
        profile = Profile.objects.get(user=user2)
        self.assertNotEqual(profile.bio, 'New bio text')  # bio also did not change
