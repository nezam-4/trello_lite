from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from boards.models import Board, BoardMembership, BoardInvitation

User = get_user_model()


class BoardFlowTests(APITestCase):
    """Core board flow tests"""
    
    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.owner = User.objects.create_user(
            email='owner@example.com',
            username='owner',
            password='Pass123!',
            is_active=True
        )
        self.member = User.objects.create_user(
            email='member@example.com',
            username='member',
            password='Pass123!',
            is_active=True
        )
        self.admin_member = User.objects.create_user(
            email='admin@example.com',
            username='admin_member',
            password='Pass123!',
            is_active=True
        )
        self.non_member = User.objects.create_user(
            email='nonmember@example.com',
            username='nonmember',
            password='Pass123!',
            is_active=True
        )
        
    def test_list_boards_shows_only_accessible_boards(self):
        """List boards: only accessible boards should be returned"""
        # Create boards
        board1 = Board.objects.create(title='Board 1', owner=self.owner)
        board2 = Board.objects.create(title='Board 2', owner=self.member)
        board3 = Board.objects.create(title='Board 3', owner=self.non_member)
        
        # Add owner as a member to board2
        BoardMembership.objects.create(
            board=board2,
            user=self.owner,
            role='member',
            status='accepted',
            invited_by=self.member  # Add invited_by
        )
        
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/v1/boards/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only board1 and board2
        board_ids = [b['id'] for b in response.data]
        self.assertIn(board1.id, board_ids)
        self.assertIn(board2.id, board_ids)
        self.assertNotIn(board3.id, board_ids)
        
    def test_create_board_success(self):
        """Create board success"""
        self.client.force_authenticate(user=self.owner)
        
        data = {
            'title': 'New Board',
            'description': 'Test board description',
            'color': '#FF0000',
            'is_public': False
        }
        
        response = self.client.post('/api/v1/boards/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify board creation
        board = Board.objects.get(title='New Board')
        self.assertEqual(board.owner, self.owner)
        self.assertEqual(board.description, 'Test board description')
        
    def test_board_detail_access_denied_for_non_member(self):
        """Board detail access: non-member should not have access"""
        board = Board.objects.create(title='Private Board', owner=self.owner)
        
        self.client.force_authenticate(user=self.non_member)
        response = self.client.get(f'/api/v1/boards/{board.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_board_update_by_owner_success(self):
        """Update board by owner"""
        board = Board.objects.create(title='Original Title', owner=self.owner)
        
        self.client.force_authenticate(user=self.owner)
        data = {'title': 'Updated Title'}
        
        response = self.client.patch(f'/api/v1/boards/{board.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        board.refresh_from_db()
        self.assertEqual(board.title, 'Updated Title')
        
    def test_board_update_by_admin_member_success(self):
        """Update board by admin member"""
        board = Board.objects.create(title='Board Title', owner=self.owner)
        BoardMembership.objects.create(
            board=board,
            user=self.admin_member,
            role='admin',
            status='accepted',
            invited_by=self.owner
        )
        
        self.client.force_authenticate(user=self.admin_member)
        data = {'title': 'Admin Updated'}
        
        response = self.client.patch(f'/api/v1/boards/{board.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_board_update_by_regular_member_fails(self):
        """Update board by regular member: should return 403"""
        board = Board.objects.create(title='Board Title', owner=self.owner)
        BoardMembership.objects.create(
            board=board,
            user=self.member,
            role='member',
            status='accepted',
            invited_by=self.owner
        )
        
        self.client.force_authenticate(user=self.member)
        data = {'title': 'Member Updated'}
        
        response = self.client.patch(f'/api/v1/boards/{board.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_remove_member_by_owner_success(self):
        """Remove member by owner"""
        board = Board.objects.create(title='Board', owner=self.owner)
        membership = BoardMembership.objects.create(
            board=board,
            user=self.member,
            role='member',
            status='accepted',
            invited_by=self.owner
        )
        
        self.client.force_authenticate(user=self.owner)
        
        response = self.client.delete(f'/api/v1/boards/{board.id}/members/{self.member.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify membership deleted
        self.assertFalse(BoardMembership.objects.filter(id=membership.id).exists())
        
    def test_leave_board_by_member_success(self):
        """Leave board by member"""
        board = Board.objects.create(title='Board', owner=self.owner)
        membership = BoardMembership.objects.create(
            board=board,
            user=self.member,
            role='member',
            status='accepted',
            invited_by=self.owner
        )
        
        self.client.force_authenticate(user=self.member)
        
        response = self.client.post(f'/api/v1/boards/{board.id}/leave/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify membership deleted
        self.assertFalse(BoardMembership.objects.filter(id=membership.id).exists())
        
    def test_owner_cannot_leave_board(self):
        """Owner cannot leave their own board"""
        board = Board.objects.create(title='Board', owner=self.owner)
        
        self.client.force_authenticate(user=self.owner)
        
        response = self.client.post(f'/api/v1/boards/{board.id}/leave/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_invite_registered_user_and_accept(self):
        """Invite a registered user and accept the invitation"""
        board = Board.objects.create(title='Board', owner=self.owner)
        
        # Invite user
        self.client.force_authenticate(user=self.owner)
        
        invite_data = {
            'identifier': 'member',  # Username
            'role': 'member'
        }
        
        response = self.client.post(f'/api/v1/boards/{board.id}/invitations/user/', invite_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify invitation was created
        invitation = BoardInvitation.objects.get(board=board, invited_by=self.owner)
        self.assertEqual(invitation.user, self.member)
        
        # Accept invitation
        self.client.force_authenticate(user=self.member)
        
        accept_data = {'action': 'accept'}
        response = self.client.post(f'/api/v1/invitations/{invitation.id}/respond/', accept_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify membership created
        membership = BoardMembership.objects.get(board=board, user=self.member)
        self.assertEqual(membership.status, 'accepted')
        self.assertEqual(membership.role, 'member')
        
        # Verify invitation marked as used
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_used)
