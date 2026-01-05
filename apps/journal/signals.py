"""
Django signals for journal app.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Entry
from .utils import update_user_streak


@receiver(post_save, sender=Entry)
def update_streak_on_entry_create(sender, instance, created, **kwargs):
    """
    Update user's writing streak when entry gets content.

    Updates streak in two cases:
    1. New entry created with content (word_count > 0)
    2. Existing empty entry updated with content (transition from 0 to >0 words)

    This allows creating empty entries for 750words.com style daily notes
    without affecting the streak until user actually writes something.

    Uses post_save signal instead of model save() to ensure
    the entry is fully saved before updating the streak.
    """
    # For newly created entries, only update if has content
    if created and instance.word_count > 0:
        update_user_streak(instance.user, instance.created_at)
    # For updated entries, check if this is the first time it has content
    elif not created and instance.word_count > 0:
        # Check if there are any other entries for this day with content
        # If this is the only entry with content for today, update streak
        from .models import Entry
        from .utils import get_user_local_date

        entry_date = get_user_local_date(instance.created_at, instance.user.timezone)
        user_last_entry_date = instance.user.last_entry_date

        # Only update streak if this day hasn't been counted yet
        if user_last_entry_date != entry_date:
            update_user_streak(instance.user, instance.created_at)


@receiver(post_save, sender=Entry)
def invalidate_dashboard_cache_on_save(sender, instance, **kwargs):
    """
    Invalidate cached dashboard stats when an entry is created or updated.
    This ensures the dashboard shows up-to-date statistics.
    """
    cache_key = f'dashboard_stats_{instance.user.id}'
    cache.delete(cache_key)


@receiver(post_delete, sender=Entry)
def invalidate_dashboard_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate cached dashboard stats when an entry is deleted.
    """
    cache_key = f'dashboard_stats_{instance.user.id}'
    cache.delete(cache_key)
