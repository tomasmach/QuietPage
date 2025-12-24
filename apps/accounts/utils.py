"""
Utility functions for the accounts app.

This module provides helper functions for user account management,
including avatar processing and display.
"""

from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
import sys


def resize_avatar(image_file, size=(512, 512)):
    """
    Resize uploaded avatar to specified dimensions.
    
    Args:
        image_file: Django UploadedFile object
        size: Tuple of (width, height) for the output image
        
    Returns:
        InMemoryUploadedFile: Resized image ready for saving
    """
    # Open the image
    img = Image.open(image_file)
    # Convert all to RGBA first for consistent handling
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Convert RGBA to RGB if necessary (for PNG with transparency)
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # Alpha channel
        img = background
    
    # Resize using high-quality Lanczos filter
    # Use thumbnail to maintain aspect ratio, then crop to exact size
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    # Create a square image with the resized image centered
    output_img = Image.new('RGB', size, (255, 255, 255))
    offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
    output_img.paste(img, offset)
    
    # Save to BytesIO
    output = BytesIO()
    output_img.save(output, format='JPEG', quality=90, optimize=True)
    output.seek(0)
    
    # Create InMemoryUploadedFile
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{image_file.name.split('.')[0]}.jpg",
        'image/jpeg',
        output.tell(),
        None
    )


def get_user_avatar_url(user):
    """
    Get the URL for a user's avatar.
    
    Returns the user's avatar URL if they have one,
    otherwise returns the URL for the default placeholder avatar.
    
    Args:
        user: User instance
        
    Returns:
        str: URL to the avatar image
    """
    if user.avatar and hasattr(user.avatar, 'url'):
        return user.avatar.url
    
    # Return placeholder avatar URL (SVG)
    # User can replace this with custom image later
    return f"{settings.STATIC_URL}images/default-avatar.png"
