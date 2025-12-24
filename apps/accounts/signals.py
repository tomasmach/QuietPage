"""
Signal handlers for the accounts app.

This module handles automatic cleanup and processing of user-related files,
such as deleting old avatars when new ones are uploaded.
"""

from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import User

import logging
logger = logging.getLogger(__name__)


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
            old_user.avatar.delete(save=False)
        except Exception:
            # Log but don't block user save
            logger.warning(
                f"Failed to delete old avatar for user {instance.pk}",
                exc_info=True
            )


@receiver(pre_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """
    Delete avatar file when user account is deleted.
    
    Ensures no orphaned files remain in storage after account deletion.
    """
    if instance.avatar:
        # Delete the avatar file from storage
        try:
            instance.avatar.delete(save=False)
        except Exception:
            logger.warning(
                f"Failed to delete avatar for user {instance.pk} during deletion",
                exc_info=True
            )
