from django.conf import settings
from .models import Board, BoardMembership

def check_user_board_limit(user):
    """Check whether the user can create a new board"""
    max_boards = getattr(settings, 'MAX_BOARDS_PER_USER', 10)
    current_boards = Board.objects.filter(owner=user).count()
    return current_boards < max_boards, max_boards - current_boards

def check_board_member_limit(board):
    """Check whether the board can accept new members"""
    max_members = getattr(settings, 'MAX_MEMBERS_PER_BOARD', 50)
    current_members = BoardMembership.objects.filter(
        board=board,
        status='accepted'
    ).count()
    return current_members < max_members, max_members - current_members

def check_user_membership_limit(user):
    """Check whether the user can join a new board"""
    max_memberships = getattr(settings, 'MAX_MEMBERSHIPS_PER_USER', 20)
    current_memberships = BoardMembership.objects.filter(
        user=user,
        status='accepted'
    ).count()
    return current_memberships < max_memberships, max_memberships - current_memberships

def get_user_limits_info(user):
    """Full user limit information"""
    return {
        'boards': {
            'current': Board.objects.filter(owner=user).count(),
            'max': getattr(settings, 'MAX_BOARDS_PER_USER', 10)
        },
        'memberships': {
            'current': BoardMembership.objects.filter(user=user, status='accepted').count(),
            'max': getattr(settings, 'MAX_MEMBERSHIPS_PER_USER', 20)
        }
    }
