from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data"""
    
    avatar_thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['avatar', 'avatar_thumbnail_url', 'bio', 'preferred_language', 'created_at', 'updated_at']
        read_only_fields = ['avatar_thumbnail_url', 'created_at', 'updated_at']
    
    def get_avatar_thumbnail_url(self, obj):
        """Get thumbnail URL from avatar path"""
        if not obj.avatar:
            return None
        
        # Get the thumbnail path
        thumbnail_path = obj.get_thumbnail_path()
        if thumbnail_path:
            # Return the URL for the thumbnail
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/{thumbnail_path}')
            return f'/media/{thumbnail_path}'
        return None


class UserSerializer(serializers.ModelSerializer):
    """Complete user serializer with profile and statistics"""
    
    # Include nested profile data (read-only)
    profile = ProfileSerializer(read_only=True)
    # Calculate user statistics
    boards_count = serializers.SerializerMethodField()
    memberships_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'created_at', 'updated_at', 'profile',
            'boards_count', 'memberships_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'boards_count', 'memberships_count']
    
    def get_boards_count(self, obj):
        """Get number of boards owned by the user"""
        return obj.get_boards_count()
    
    def get_memberships_count(self, obj):
        """Get number of board memberships for the user"""
        return obj.get_memberships_count()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information safely"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']
        read_only_fields = ['email']
    
    def validate_username(self, value):
        """Ensure username uniqueness excluding current user"""
        user = self.instance
        if CustomUser.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError(_("A user with this username already exists."))
        return value


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password confirmation"""
    
    # Password fields with minimum length requirement
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ["email", "username", "first_name", "last_name", "password1", "password2"]

    def validate(self, attrs):
        """Validate password confirmation and complexity"""
        pwd1 = attrs.get("password1")
        pwd2 = attrs.get("password2")
        
        # Check if passwords match
        if pwd1 != pwd2:
            raise serializers.ValidationError({"password2": _("Passwords do not match.")})
        
        # Validate password complexity using Django's validators
        validate_password(pwd1)
        return attrs

    def create(self, validated_data):
        """Create user with hashed password and profile"""
        # Remove password confirmation field
        validated_data.pop("password2")
        password = validated_data.pop("password1")
        
        # Create user with hashed password
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password with old password verification"""
    
    # Password fields for secure password change
    old_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, min_length=8)
    
    def validate_old_password(self, value):
        """Verify the current password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Old password is incorrect."))
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation and complexity"""
        pwd1 = attrs.get("new_password1")
        pwd2 = attrs.get("new_password2")
        
        # Check if new passwords match
        if pwd1 != pwd2:
            raise serializers.ValidationError({"new_password2": _("New passwords do not match.")})
        
        # Validate new password complexity
        validate_password(pwd1)
        return attrs
    
    def save(self):
        """Update user password with new hashed password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user
