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
    Update user's writing streak when a new entry is created.

    Uses post_save signal instead of model save() to ensure
    the entry is fully saved before updating the streak.
    """
    if created:
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
