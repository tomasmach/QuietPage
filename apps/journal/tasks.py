"""
Celery tasks for journal app.

This module contains async tasks for:
- Email change request cleanup
- Weekly data cleanup
- User data export (GDPR compliance)
- Daily statistics aggregation

These tasks help maintain data hygiene and provide user services.
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from celery import shared_task

from apps.accounts.models import EmailChangeRequest
from apps.journal.models import Entry
from apps.journal.utils import upload_export_to_secure_storage, send_export_link_email

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, ignore_result=True)
def cleanup_expired_email_requests(self):
    """
    Delete expired EmailChangeRequest records.

    Removes unverified email change requests that are older than their
    expiration time. This keeps the database clean and removes stale data.

    Runs daily at 2:00 AM (configured in CELERY_BEAT_SCHEDULE).

    Returns:
        dict: {'deleted': int, 'errors': int}
    """
    try:
        now = timezone.now()

        # Find expired, unverified requests
        expired_requests = EmailChangeRequest.objects.filter(
            is_verified=False,
            expires_at__lt=now
        )

        count = expired_requests.count()
        deleted, _ = expired_requests.delete()

        logger.info(f"Cleaned up {count} expired email change requests")
        return {'deleted': count, 'errors': 0}

    except Exception as e:
        logger.error(f"Failed to cleanup expired email requests: {e}", exc_info=True)
        return {'deleted': 0, 'errors': 1}


@shared_task(bind=True, ignore_result=True)
def weekly_cleanup(self):
    """
    Perform weekly maintenance cleanup tasks.

    Currently performs:
    1. Cleanup of very old unverified email change requests (>30 days)
    2. Log file rotation indicator

    Future additions could include:
    - Orphaned file cleanup (avatars from deleted users)
    - Session cleanup
    - Cache cleanup

    Runs every Sunday at 3:00 AM (configured in CELERY_BEAT_SCHEDULE).

    Returns:
        dict: Cleanup statistics
    """
    stats = {'old_email_requests_deleted': 0, 'errors': 0}

    try:
        # Cleanup very old email change requests (even if not expired)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        old_requests = EmailChangeRequest.objects.filter(
            created_at__lt=thirty_days_ago,
            is_verified=False
        )

        count = old_requests.count()
        old_requests.delete()
        stats['old_email_requests_deleted'] = count

        logger.info(f"Weekly cleanup complete: {stats}")

        # Log rotation reminder (manual process for now)
        logger.info("Weekly cleanup: Consider rotating log files")

        return stats

    except Exception as e:
        logger.error(f"Weekly cleanup failed: {e}", exc_info=True)
        stats['errors'] = 1
        return stats


@shared_task(bind=True, max_retries=2, default_retry_delay=300, ignore_result=True)
def export_user_data(self, user_id):
    """
    Export all user data for GDPR compliance.

    Creates a JSON export containing:
    - User profile information
    - All journal entries (decrypted)
    - Statistics and preferences

    The export is saved to secure storage and a download link is emailed
    to the user. No decrypted data is returned from this task to prevent
    sensitive information from being persisted in the Celery result backend.

    Args:
        user_id (int): ID of user requesting data export

    Returns:
        None: Task uses ignore_result=True for security

    Raises:
        Exception: If export fails (task will retry)

    Security:
        - Uses ignore_result=True to prevent decrypted data in result backend
        - Stores export in secure file storage (not in Redis/database)
        - Sends time-limited download link via email
    """
    try:
        user = User.objects.get(pk=user_id)

        # Export user profile
        user_data = {
            'export_timestamp': timezone.now().isoformat(),
            'user': {
                'username': user.username,
                'email': user.email,
                'bio': user.bio,
                'date_joined': user.date_joined.isoformat(),
                'timezone': str(user.timezone),
                'preferred_language': user.preferred_language,
                'preferred_theme': user.preferred_theme,
            },
            'preferences': {
                'daily_word_goal': user.daily_word_goal,
                'preferred_writing_time': user.preferred_writing_time,
                'reminder_enabled': user.reminder_enabled,
                'reminder_time': user.reminder_time.isoformat() if user.reminder_time else None,
                'email_notifications': user.email_notifications,
            },
            'statistics': {
                'current_streak': user.current_streak,
                'longest_streak': user.longest_streak,
                'last_entry_date': user.last_entry_date.isoformat() if user.last_entry_date else None,
            },
            'entries': []
        }

        # Export all journal entries
        entries = Entry.objects.filter(user=user).order_by('created_at')

        for entry in entries:
            entry_data = {
                'id': str(entry.id),
                'title': entry.title,
                'content': entry.get_content(),  # Decrypted with per-user key
                'word_count': entry.word_count,
                'mood_rating': entry.mood_rating,
                'tags': [tag.name for tag in entry.tags.all()],
                'is_favorite': entry.is_favorite,
                'created_at': entry.created_at.isoformat(),
                'updated_at': entry.updated_at.isoformat(),
            }
            user_data['entries'].append(entry_data)

        logger.info(f"Data export completed for user {user.username}: {len(entries)} entries")

        # Save export to secure storage
        storage_path = upload_export_to_secure_storage(user_id, user_data)

        # Send download link via email
        send_export_link_email(user.email, user.username, storage_path)

        logger.info(f"Export stored and email sent for user {user.username}")

        # Don't return user_data - ignore_result=True prevents it from being stored
        # in the Celery result backend (security measure)
        return None

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for data export")
        return None

    except Exception as e:
        logger.error(f"Data export failed for user {user_id}: {e}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, ignore_result=True)
def aggregate_daily_statistics(self, user_id):
    """
    Aggregate daily statistics for a user.

    This is a placeholder for future implementation of daily stats rollup.
    Could be used to pre-calculate statistics to improve dashboard performance.

    Args:
        user_id (int): User ID to aggregate statistics for

    Returns:
        dict: Aggregated statistics

    Note:
        Currently not used. Can be implemented later if dashboard queries
        become slow due to large number of entries.
    """
    try:
        user = User.objects.get(pk=user_id)
        entries = Entry.objects.filter(user=user)

        stats = {
            'total_entries': entries.count(),
            'total_words': sum(e.word_count for e in entries),
            'favorite_entries': entries.filter(is_favorite=True).count(),
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
        }

        logger.debug(f"Daily statistics aggregated for user {user.username}: {stats}")
        return stats

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for statistics aggregation")
        return None

    except Exception as e:
        logger.error(f"Statistics aggregation failed for user {user_id}: {e}", exc_info=True)
        return None
