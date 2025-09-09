from celery import shared_task
from django.core.files.storage import default_storage
from PIL import Image
import io
import os


@shared_task
def create_avatar_thumbnail(profile_id):
    """
    Create thumbnail for avatar asynchronously
    """
    from .models import Profile
    
    try:
        profile = Profile.objects.get(id=profile_id)
        
        if not profile.avatar:
            return f"No avatar found for profile {profile_id}"
            
        # Open the image
        image = Image.open(profile.avatar)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Create thumbnail (150x150 pixels)
        thumbnail_size = (150, 150)
        image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        
        # Create a square thumbnail by cropping/padding
        thumb_image = Image.new('RGB', thumbnail_size, (255, 255, 255))
        
        # Calculate position to center the image
        x = (thumbnail_size[0] - image.size[0]) // 2
        y = (thumbnail_size[1] - image.size[1]) // 2
        thumb_image.paste(image, (x, y))
        
        # Save to BytesIO
        thumb_io = io.BytesIO()
        thumb_image.save(thumb_io, format='JPEG', quality=85)
        thumb_io.seek(0)
        
        # Generate thumbnail path
        thumbnail_path = profile.get_thumbnail_path()
        
        # Save the thumbnail alongside the original avatar
        default_storage.save(thumbnail_path, thumb_io)
        
        return f"Thumbnail created successfully for profile {profile_id}"
        
    except Profile.DoesNotExist:
        return f"Profile {profile_id} not found"
    except Exception as e:
        return f"Error creating thumbnail for profile {profile_id}: {str(e)}"
