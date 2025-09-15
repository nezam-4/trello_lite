from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from boards.models import Board, BoardMembership
from lists.models import List
from tasks.models import Task

User = get_user_model()


class TaskFlowTests(APITestCase):
    """Core task flow tests """
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.owner = User.objects.create_user(
            email='owner@example.com',
            username='owner',
            password='Pass123!',
            is_active=True
        )
        self.member1 = User.objects.create_user(
            email='member1@example.com',
            username='member1',
            password='Pass123!',
            is_active=True
        )
        self.member2 = User.objects.create_user(
            email='member2@example.com',
            username='member2',
            password='Pass123!',
            is_active=True
        )
        self.non_member = User.objects.create_user(
            email='nonmember@example.com',
            username='nonmember',
            password='Pass123!',
            is_active=True
        )
        
        # Create board and lists
        self.board = Board.objects.create(title='Project Board', owner=self.owner)
        self.list1 = List.objects.create(board=self.board, title='To Do', position=4)
        self.list2 = List.objects.create(board=self.board, title='In Progress', position=5)
        self.list3 = List.objects.create(board=self.board, title='Done', position=6)
        
        # Add members
        BoardMembership.objects.create(
            board=self.board,
            user=self.member1,
            role='member',
            status='accepted',
            invited_by=self.owner
        )
        BoardMembership.objects.create(
            board=self.board,
            user=self.member2,
            role='member',
            status='accepted',
            invited_by=self.owner
        )
        
    def test_create_task_by_member_success(self):
        """Create task by board member"""
        self.client.force_authenticate(user=self.member1)
        
        data = {
            'title': 'New Task'
        }
        
        response = self.client.post(f'/api/v1/tasks/lists/{self.list1.id}/tasks/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify task creation
        task = Task.objects.get(title='New Task')
        self.assertEqual(task.list, self.list1)
        self.assertEqual(task.created_by, self.member1)
        self.assertEqual(task.position, 1)
        
    def test_create_task_by_owner_success(self):
        """Create task by board owner"""
        self.client.force_authenticate(user=self.owner)
        
        data = {
            'title': 'Owner Task'
        }
        
        response = self.client.post(f'/api/v1/tasks/lists/{self.list1.id}/tasks/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_create_task_by_non_member_fails(self):
        """Create task by non-member: should be rejected (403)"""
        self.client.force_authenticate(user=self.non_member)
        
        data = {
            'title': 'Unauthorized Task'
        }
        
        response = self.client.post(f'/api/v1/tasks/lists/{self.list1.id}/tasks/', data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_update_task_assign_to_member_success(self):
        """Update task: assign to board members"""
        task = Task.objects.create(
            title='Task to Assign',
            list=self.list1,
            created_by=self.owner,
            position=4
        )
        
        self.client.force_authenticate(user=self.owner)
        
        data = {
            'assigned_to': [self.member1.id, self.member2.id]
        }
        
        response = self.client.patch(f'/api/v1/tasks/tasks/{task.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify assignment
        task.refresh_from_db()
        assigned_users = list(task.assigned_to.all())
        self.assertIn(self.member1, assigned_users)
        self.assertIn(self.member2, assigned_users)
        
    def test_update_task_assign_to_non_member_fails(self):
        """Update task: assigning to a non-member should be rejected (400)"""
        task = Task.objects.create(
            title='Task',
            list=self.list1,
            created_by=self.owner,
            position=4
        )
        
        self.client.force_authenticate(user=self.owner)
        
        data = {
            'assigned_to': [self.non_member.id]
        }
        
        response = self.client.patch(f'/api/v1/tasks/tasks/{task.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_update_task_due_date_and_priority(self):
        """Update due_date and priority"""
        task = Task.objects.create(
            title='Task with Deadline',
            list=self.list1,
            created_by=self.owner,
            position=4
        )
        
        self.client.force_authenticate(user=self.member1)
        
        future_date = timezone.now().date() + timedelta(days=7)
        data = {
            'due_date': future_date.isoformat(),
            'priority': 'high'
        }
        
        response = self.client.patch(f'/api/v1/tasks/tasks/{task.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertEqual(task.due_date, future_date)
        self.assertEqual(task.priority, 'high')
        
    def test_move_task_to_another_list(self):
        """Move task to another list"""
        task = Task.objects.create(
            title='Task to Move',
            list=self.list1,
            created_by=self.owner,
            position=4
        )
        
        self.client.force_authenticate(user=self.member1)
        
        data = {
            'new_list': self.list2.id,
            'new_position': 4
        }
        
        response = self.client.post(f'/api/v1/tasks/tasks/{task.id}/move/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify moving
        task.refresh_from_db()
        self.assertEqual(task.list, self.list2)
        self.assertEqual(task.position, 4)
        
    def test_move_task_position_within_same_list(self):
        """Move task position within the same list"""
        # Create multiple tasks
        task1 = Task.objects.create(title='Task 1', list=self.list1, created_by=self.owner, position=4)
        task2 = Task.objects.create(title='Task 2', list=self.list1, created_by=self.owner, position=5)
        task3 = Task.objects.create(title='Task 3', list=self.list1, created_by=self.owner, position=6)
        
        self.client.force_authenticate(user=self.member1)
        
        # Move task3 to position 1
        data = {'new_position': 4}
        
        response = self.client.post(f'/api/v1/tasks/tasks/{task3.id}/move/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new positions
        task1.refresh_from_db()
        task2.refresh_from_db()
        task3.refresh_from_db()
        
        self.assertEqual(task3.position, 4)
        self.assertEqual(task1.position, 5)
        self.assertEqual(task2.position, 6)
        
    def test_toggle_task_complete_status(self):
        """Toggle task complete status"""
        task = Task.objects.create(
            title='Task to Complete',
            list=self.list1,
            created_by=self.owner,
            position=4,
            is_completed=False
        )
        
        self.client.force_authenticate(user=self.member1)
        
        # Mark as completed
        response = self.client.post(f'/api/v1/tasks/tasks/{task.id}/toggle-complete/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertTrue(task.is_completed)
        self.assertIsNotNone(task.completed_at)
        
        # Toggle back to incomplete
        response = self.client.post(f'/api/v1/tasks/tasks/{task.id}/toggle-complete/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertFalse(task.is_completed)
        self.assertIsNone(task.completed_at)
        
    def test_delete_task_by_creator_success(self):
        """Delete task by creator"""
        task = Task.objects.create(
            title='Task to Delete',
            list=self.list1,
            created_by=self.member1,
            position=1
        )
        
        self.client.force_authenticate(user=self.member1)
        
        response = self.client.delete(f'/api/v1/tasks/tasks/{task.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        self.assertFalse(Task.objects.filter(id=task.id).exists())
        
    def test_delete_task_by_board_owner_success(self):
        """Delete task by board owner"""
        task = Task.objects.create(
            title='Member Task',
            list=self.list1,
            created_by=self.member1,
            position=4
        )
        
        self.client.force_authenticate(user=self.owner)
        
        response = self.client.delete(f'/api/v1/tasks/tasks/{task.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_delete_task_by_other_member_fails(self):
        """Delete task by other member: should be rejected (403)"""
        task = Task.objects.create(
            title='Task',
            list=self.list1,
            created_by=self.member1,
            position=4
        )
        
        self.client.force_authenticate(user=self.member2)
        
        response = self.client.delete(f'/api/v1/tasks/tasks/{task.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_task_access_by_non_member_fails(self):
        """Task access by non-member: should be rejected (403)"""
        task = Task.objects.create(
            title='Private Task',
            list=self.list1,
            created_by=self.owner,
            position=4
        )
        
        self.client.force_authenticate(user=self.non_member)
        
        # Try to get details
        response = self.client.get(f'/api/v1/tasks/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to update
        response = self.client.patch(f'/api/v1/tasks/tasks/{task.id}/', {'title': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to move
        response = self.client.post(f'/api/v1/tasks/tasks/{task.id}/move/', {'new_position': 5})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
