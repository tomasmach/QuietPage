"""
Django signals for journal app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Entry
from .utils import update_user_streak


@receiver(post_save, sender=Entry)
def update_streak_on_entry_create(sender, instance, created, **kwargs):
    """
    Update user's writing streak when a new entry is created.
    
    Uses post_save signal instead of model save() to ensure
    the entry is fully saved before updating the streak.
    """
    if created:
        update_user_streak(instance.user, instance.created_at)
