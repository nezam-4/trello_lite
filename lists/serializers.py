from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import List


class ListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing lists.
    - Used for showing list summaries in list views.
    - Contains main list information
    - Optimized for speed and minimum payload size.
    """

    class Meta:
        model = List
        fields = ['id', 'title', 'color', 'position', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'position']


class ListDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for list detail view.
    - Shows all information of a specific list.
    - Used on the list details page.
    """
    class Meta:
        model = List
        fields = ['id', 'title', 'color', 'position', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ListCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new list.
    - Validates incoming data to create a list.
    - Automatically assigns position.
    """
    
    class Meta:
        model = List
        fields = ['title', 'color', 'board']


class ListUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a list.
    - Used to edit existing list information.
    - Includes only editable fields.
    - Position updates handled separately via move endpoint.
    """
    
    class Meta:
        model = List
        fields = ['title','color']


class ListMoveSerializer(serializers.Serializer):
    """
    Serializer for moving a list to a new position.
    - Handles position updates within the same board.
    - Validates position range.
    """
    position = serializers.IntegerField(min_value=1)
