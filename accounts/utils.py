"""
Utility functions for profile and thumbnail management
"""
from django.core.files.storage import default_storage
import os


def get_thumbnail_url_from_avatar_url(avatar_url):
    """
    Get thumbnail URL from avatar URL by adding _thumbnail before extension
    
    Example:
    avatar_url = "/media/avatar/09/user_1_abc123.jpg"
    returns = "/media/avatar/09/user_1_abc123_thumbnail.jpg"
    """
    if not avatar_url:
        return None
    
    # Remove /media/ prefix if present
    if avatar_url.startswith('/media/'):
        avatar_path = avatar_url[7:]  # Remove '/media/'
    else:
        avatar_path = avatar_url
    
    # Add _thumbnail before extension
    name, ext = os.path.splitext(avatar_path)
    thumbnail_path = f"{name}_thumbnail{ext}"
    
    return f"/media/{thumbnail_path}"


def check_thumbnail_exists(avatar_path):
    """
    Check if thumbnail exists for given avatar path
    """
    if not avatar_path:
        return False
    
    name, ext = os.path.splitext(avatar_path)
    thumbnail_path = f"{name}_thumbnail{ext}"
    
    return default_storage.exists(thumbnail_path)


def create_thumbnail_sync(profile_id):
    """
    Create thumbnail synchronously (for immediate use if needed)
    """
    from .tasks import create_avatar_thumbnail
    
    # Call the task function directly (not async)
    return create_avatar_thumbnail(profile_id)


def get_profile_images_info(user):
    """
    Get complete profile images information for a user
    
    Returns:
    {
        'avatar_url': '/media/avatar/09/user_1_abc123.jpg',
        'thumbnail_url': '/media/avatar/09/user_1_abc123_thumbnail.jpg',
        'has_avatar': True,
        'has_thumbnail': True
    }
    """
    try:
        profile = user.profile
        
        result = {
            'avatar_url': None,
            'thumbnail_url': None,
            'has_avatar': False,
            'has_thumbnail': False
        }
        
        if profile.avatar:
            result['avatar_url'] = profile.avatar.url
            result['has_avatar'] = True
            
            # Generate thumbnail URL
            thumbnail_url = get_thumbnail_url_from_avatar_url(profile.avatar.url)
            if thumbnail_url:
                result['thumbnail_url'] = thumbnail_url
                # Check if thumbnail actually exists
                result['has_thumbnail'] = check_thumbnail_exists(profile.avatar.name)
        
        return result
        
    except Exception:
        return {
            'avatar_url': None,
            'thumbnail_url': None,
            'has_avatar': False,
            'has_thumbnail': False
        }
