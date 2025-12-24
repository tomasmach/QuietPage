"""
Signal handlers for the accounts app.

This module handles automatic cleanup and processing of user-related files,
such as deleting old avatars when new ones are uploaded.
"""

import os
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import User


@receiver(pre_save, sender=User)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    """
    Delete old avatar file when user uploads a new one.
    
    This prevents accumulation of unused avatar files in storage.
    Only runs when an existing user updates their avatar.
    """
    if not instance.pk:
        # New user, no old avatar to delete
        return
    
    try:
        old_user = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        # User doesn't exist yet
        return
    
    # Check if avatar has changed
    if old_user.avatar and old_user.avatar != instance.avatar:
        # Delete the old file from storage
        try:
            if os.path.isfile(old_user.avatar.path):
                os.remove(old_user.avatar.path)
        except (OSError, ValueError, NotImplementedError):
            # OSError: File deletion failed
            # ValueError/NotImplementedError: Remote storage doesn't support .path
            pass


@receiver(pre_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """
    Delete avatar file when user account is deleted.
    
    Ensures no orphaned files remain in storage after account deletion.
    """
    if instance.avatar:
        # Delete the avatar file from storage
        try:
            if os.path.isfile(instance.avatar.path):
                os.remove(instance.avatar.path)
        except (OSError, ValueError, NotImplementedError):
            pass
