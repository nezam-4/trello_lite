from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from boards.models import Board, BoardMembership
from lists.models import List

User = get_user_model()


class ListFlowTests(APITestCase):
    """Core list flow tests"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.owner = User.objects.create_user(
            email='owner@example.com',
            username='owner',
            password='Pass123!',
            is_active=True
        )
        self.admin_member = User.objects.create_user(
            email='admin@example.com',
            username='admin_member',
            password='Pass123!',
            is_active=True
        )
        self.regular_member = User.objects.create_user(
            email='member@example.com',
            username='member',
            password='Pass123!',
            is_active=True
        )
        self.non_member = User.objects.create_user(
            email='nonmember@example.com',
            username='nonmember',
            password='Pass123!',
            is_active=True
        )
        
        # Create board and memberships
        self.board = Board.objects.create(title='Test Board', owner=self.owner)
        
        BoardMembership.objects.create(
            board=self.board,
            user=self.admin_member,
            role='admin',
            status='accepted',
            invited_by=self.owner
        )
        BoardMembership.objects.create(
            board=self.board,
            user=self.regular_member,
            role='member',
            status='accepted',
            invited_by=self.owner
        )
        
    def test_create_list_by_owner_success(self):
        """Create list by board owner"""
        self.client.force_authenticate(user=self.owner)
        
        data = {
            'title': 'To Do',
            'color': '#FF0000'
        }
        
        response = self.client.post(f'/api/v1/boards/{self.board.id}/lists/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify list creation
        list_obj = List.objects.get(title='To Do')
        self.assertEqual(list_obj.board, self.board)
        # position should be 4 because three default lists (Todo, Doing, Done) are created on board creation
        self.assertEqual(list_obj.position, 4)
        
    def test_create_list_by_admin_success(self):
        """Create list by board admin"""
        self.client.force_authenticate(user=self.admin_member)
        
        data = {
            'title': 'In Progress',
            'color': '#00FF00'
        }
        
        response = self.client.post(f'/api/v1/boards/{self.board.id}/lists/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_create_list_by_regular_member_fails(self):
        """Create list by regular member: should be rejected (403)"""
        self.client.force_authenticate(user=self.regular_member)
        
        data = {
            'title': 'Done',
            'color': '#0000FF'
        }
        
        response = self.client.post(f'/api/v1/boards/{self.board.id}/lists/', data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_get_list_detail_by_member_success(self):
        """Get list detail by board member"""
        list_obj = List.objects.create(
            board=self.board,
            title='Test List',
            position=1
        )
        
        self.client.force_authenticate(user=self.regular_member)
        
        response = self.client.get(f'/api/v1/lists/{list_obj.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test List')
        
    def test_update_list_by_owner_success(self):
        """Update list by owner"""
        list_obj = List.objects.create(
            board=self.board,
            title='Original Title',
            position=1
        )
        
        self.client.force_authenticate(user=self.owner)
        
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/v1/lists/{list_obj.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        list_obj.refresh_from_db()
        self.assertEqual(list_obj.title, 'Updated Title')
        
    def test_update_list_by_regular_member_fails(self):
        """Update list by regular member: should be rejected (403)"""
        list_obj = List.objects.create(
            board=self.board,
            title='Test List',
            position=1
        )
        
        self.client.force_authenticate(user=self.regular_member)
        
        data = {'title': 'Hacked Title'}
        response = self.client.patch(f'/api/v1/lists/{list_obj.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_list_by_admin_success(self):
        """Delete list by admin"""
        list_obj = List.objects.create(
            board=self.board,
            title='To Delete',
            position=1
        )
        
        self.client.force_authenticate(user=self.admin_member)
        
        response = self.client.delete(f'/api/v1/lists/{list_obj.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        self.assertFalse(List.objects.filter(id=list_obj.id).exists())
        
    def test_move_list_position(self):
        """Move list position"""
        # Create multiple lists
        list1 = List.objects.create(board=self.board, title='List 4', position=4)
        list2 = List.objects.create(board=self.board, title='List 5', position=5)
        list3 = List.objects.create(board=self.board, title='List 6', position=6)
        
        self.client.force_authenticate(user=self.owner)
        
        # Move list3 to position 1
        data = {'position': 4}
        response = self.client.post(f'/api/v1/lists/{list3.id}/move/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new positions
        list1.refresh_from_db()
        list2.refresh_from_db()
        list3.refresh_from_db()
        
        self.assertEqual(list3.position, 4)
        self.assertEqual(list1.position, 5)
        self.assertEqual(list2.position, 6)
        
    def test_move_list_by_regular_member_fails(self):
        """Move list by regular member: should be rejected (403)"""
        list_obj = List.objects.create(board=self.board, title='List', position=1)
        
        self.client.force_authenticate(user=self.regular_member)
        
        data = {'position': 2}
        response = self.client.post(f'/api/v1/lists/{list_obj.id}/move/', data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
