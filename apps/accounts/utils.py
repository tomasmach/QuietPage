"""
Utility functions for the accounts app.

This module provides helper functions for user account management,
including avatar processing, display, and email verification.
"""

from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.template.loader import render_to_string
from django.urls import reverse

import logging

logger = logging.getLogger(__name__)

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
    output_size = output.tell()
    output.seek(0)
    
    # Create InMemoryUploadedFile
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{image_file.name.split('.')[0]}.jpg",
        'image/jpeg',
        output_size,
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


# ============================================
# EMAIL VERIFICATION UTILITIES
# ============================================


def generate_email_verification_token(user_id, new_email):
    """
    Generate a cryptographically signed token for email verification.
    
    Uses Django's TimestampSigner for security. Token contains user_id and new_email,
    and has built-in expiration checking.
    
    Args:
        user_id: ID of the user requesting email change
        new_email: The new email address to verify
        
    Returns:
        str: Signed token that can be safely sent in URLs
    """
    signer = TimestampSigner()
    value = f"{user_id}:{new_email}"
    token = signer.sign(value)
    return token


def verify_email_change_token(token, max_age=86400):
    """
    Verify and decode an email verification token.
    
    Args:
        token: The signed token to verify
        max_age: Maximum age in seconds (default: 86400 = 24 hours)
        
    Returns:
        tuple: (user_id, new_email) if valid, (None, None) if invalid/expired
    """
    signer = TimestampSigner()
    try:
        # Unsign the token with expiration check
        original = signer.unsign(token, max_age=max_age)
        # Parse the value
        user_id, new_email = original.split(':', 1)
        return int(user_id), new_email
    except (BadSignature, SignatureExpired, ValueError):
        return None, None


def send_email_verification(user, new_email, request):
    """
    Send email verification link to the new email address.
    
    Args:
        user: User instance requesting the change
        new_email: The new email address to verify
        request: HTTP request object (needed for building absolute URL)
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Generate verification token
    token = generate_email_verification_token(user.id, new_email)
    
    # Build verification URL
    verification_path = reverse('accounts:email-verify', kwargs={'token': token})
    verification_url = request.build_absolute_uri(verification_path)
    
    # Prepare email context
    context = {
        'user': user,
        'new_email': new_email,
        'verification_url': verification_url,
        'expiry_hours': 24,
    }
    
    # Render email templates
    html_message = render_to_string('accounts/emails/email_verification.html', context)
    plain_message = render_to_string('accounts/emails/email_verification.txt', context)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@quietpage.com')
    
    # Send email
    try:
        send_mail(
            subject='QuietPage - Potvrzení změny e-mailu',
            message=plain_message,
            from_email=from_email,
            recipient_list=[new_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send verification email to {new_email}: {e}", exc_info=True)
        return False
    else:
        return True
