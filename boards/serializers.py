from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Board, BoardMembership, BoardInvitation, BoardActivity
from .utils import check_user_board_limit, check_board_member_limit, check_user_membership_limit
from rest_framework.validators import UniqueTogetherValidator
from django.db.models import Q
User = get_user_model()


class BoardMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying board members.
    - Shows information about users who are members of a board.
    - Includes username, email, full name, role and membership status.
    - Read-only.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = BoardMembership
        fields = ['id', 'username', 'email', 'full_name', 'role', 'status', 'created_at']


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing boards.
    - Used for showing board summaries in list views.
    - Contains main board information + member count.
    - Optimised for speed and minimum payload size.
    """
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    members_count = serializers.SerializerMethodField()
    current_user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'description', 'color', 'is_public', 'owner_username', 
                 'members_count', 'current_user_role', 'created_at', 'updated_at']
    
    def get_members_count(self, obj):
        """Calculate active board member count"""
        return obj.active_members_count



    def get_current_user_role(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        user = request.user
        if obj.owner_id == user.id:
            return 'owner'
        membership = obj.memberships.filter(user=user, status='accepted').first()
        if membership:
            return membership.role
        return None


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for board detail view.
    - Shows all information of a specific board.
    - Includes full member list, capabilities and limits.
    - Used on the board details page.
    """
    owner = serializers.StringRelatedField(read_only=True)
    members = BoardMemberSerializer(source='memberships', many=True, read_only=True)
    members_count = serializers.SerializerMethodField()
    can_add_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'description', 'color', 'is_public', 'owner', 
                 'members', 'members_count', 'can_add_member', 'created_at', 'updated_at']
    
    def get_members_count(self, obj):
        """Calculate active board member count"""
        return obj.active_members_count
    
    def get_can_add_member(self, obj):
        """Check if a new member can be added to the board"""
        return obj.can_add_member()


class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new board.
    - Validates incoming data to create a board.
    - Checks the user's board-creation quota.
    - Automatically assigns the owner.
    """
    
    class Meta:
        model = Board
        fields = ['title', 'description', 'color', 'is_public']
    
    def validate(self, attrs):
        """
        Validate input data.
        - Checks the user's board-creation quota.
        """
        user = self.context['request'].user
        can_create, remaining = check_user_board_limit(user)
        
        if not can_create:
            raise serializers.ValidationError(
                _(f"You have reached the maximum number of boards allowed. You can create {remaining} more.")
            )
        
        return attrs
    
    def create(self, validated_data):
        """Automatically set the board owner on creation."""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a board.
    - Used to edit existing board information.
    - Includes only editable fields.
    - Board owner cannot be changed.
    """
    
    class Meta:
        model = Board
        fields = ['title', 'description', 'color', 'is_public']


class BoardMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for managing board memberships.
    - Shows membership information of users in boards.
    - Includes role, status and join date.
    - Used for board member management.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    board_title = serializers.CharField(source='board.title', read_only=True)
    
    class Meta:
        model = BoardMembership
        fields = ['id', 'user_username', 'board_title', 'role', 'status', 'created_at', 'response_at']


class BoardInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for board invitations.
    il.
    - Validates email and ch- Handles inviting users to a board via emaecks limits.
    - Creates an invitation with a unique token.
    """
    invited_by_username = serializers.CharField(source='invited_by.username', read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    board_title = serializers.CharField(source='board.title', read_only=True)
    
    class Meta:
        model = BoardInvitation
        fields = ['id', 'board_title', 'user', 'invited_by_username', 
                 'role', 'is_used', 'expires_at','status', 'created_at','invited_email']
        read_only_fields = ['token', 'is_used', ]

    
    def validate_invited_email(self, value):
        """
        Validate invitee's email.
        - Checks if a user with this email exists.
        """
        user = User.objects.filter(email=value).first()
        if user:
            raise serializers.ValidationError(_("This user is already signed up"))

        return value
    
    def validate(self, attrs):
        """
        Validate invitation data.
        - Checks board member limit.
        """
        board = self.context.get('board')
        
        # check duplicate invitation
        invited_email = attrs.get('invited_email')
        if board and invited_email:
            if BoardInvitation.objects.filter(board=board, invited_email=invited_email, is_used=False).exists():
                raise serializers.ValidationError(
                    _("An invitation has already been sent to this email for this board.")
                )
        # check board limitation and user 
        if board:
            can_add_member, remaining_slots = check_board_member_limit(board)
            if not can_add_member:
                raise serializers.ValidationError(
                    _(f"Board has reached the maximum number of members. {remaining_slots} slots remaining.")
                )
        return attrs
    
    def create(self, validated_data):
        """
        Create a new invitation.
        - Sets board and inviter.
        """
        board = self.context['board']
        validated_data['board'] = board
        validated_data['invited_by'] = self.context['request'].user

        # Remove old processed invitations to avoid unique constraint conflicts
        BoardInvitation.objects.filter(board=board, invited_email=validated_data.get('invited_email'), is_used=True).delete()
        
        return super().create(validated_data)


class BoardUserInvitationSerializer(serializers.Serializer):
    """
    Serializer for inviting an already-registered user to a board using username **or** email.
    Fields:
        identifier: str   -> username *or* email of the target user
        role: str         -> optional, defaults to "member"
    """
    identifier = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=[('admin', 'Admin'), ('member', 'Member')], default='member')

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        board = self.context.get('board')
        if not board:
            raise serializers.ValidationError("Board context missing.")

        # Find user by username or email
        try:
            target_user = User.objects.get(Q(username=identifier) | Q(email=identifier))
        except User.DoesNotExist:
            raise serializers.ValidationError(_("No registered user with this username or email was found."))

        # Ensure target user is not already a member
        if BoardMembership.objects.filter(board=board, user=target_user, status='accepted').exists():
            raise serializers.ValidationError(_("This user is already a member of the board."))

        # Ensure there isn't already a pending invitation for this user
        if BoardInvitation.objects.filter(board=board, user=target_user, is_used=False).exists():
            raise serializers.ValidationError(_("An invitation has already been sent to this user."))

        # Check board member limit
        can_add_member, remaining_slots = check_board_member_limit(board)
        if not can_add_member:
            raise serializers.ValidationError(_("Board has reached the maximum number of members."))

        # Check user membership limit
        can_join, remaining_memberships = check_user_membership_limit(target_user)
        if not can_join:
            raise serializers.ValidationError(_("The user has reached their maximum number of board memberships."))

        attrs['target_user'] = target_user
        return attrs

class BoardActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for board activities.
    - Shows the activity history performed on a board.
    - Includes action type, acting user and description.
    - Used to display activity logs.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = BoardActivity
        fields = ['id', 'action', 'action_display', 'user_username', 'description', 'created_at']
