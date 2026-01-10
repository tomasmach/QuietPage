"""
Celery tasks for accounts app.

This module contains async tasks for:
- Email sending (generic and specific)
- Email verification
- Daily writing reminders

All email tasks have retry logic and proper error handling.
"""

import logging
from datetime import time, datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from celery import shared_task

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_async(self, subject, plain_message, recipient_list, from_email=None):
    """
    Generic async email sender with retry logic.

    Args:
        subject (str): Email subject line
        plain_message (str): Plain text email body
        recipient_list (list): List of recipient email addresses
        from_email (str, optional): Sender email (uses DEFAULT_FROM_EMAIL if not provided)

    Returns:
        int: Number of emails sent successfully

    Raises:
        Exception: If email sending fails after retries
    """
    try:
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        # Send plain text email
        sent = send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False
        )

        logger.info(f"Email sent successfully: {subject} to {recipient_list}")
        return sent

    except Exception as e:
        logger.error(f"Email sending failed: {subject} to {recipient_list} - {e}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_async(self, user_id, new_email, verification_url):
    """
    Send email verification link to new email address.

    This task is called when a user changes their email address.
    It sends a plain text verification email.

    Args:
        user_id (int): User ID requesting the change
        new_email (str): New email address to verify
        verification_url (str): Full verification URL with token

    Returns:
        bool: True if email sent successfully

    Raises:
        Exception: If email sending fails after retries
    """
    try:
        user = User.objects.get(pk=user_id)

        # Prepare email context
        context = {
            'user': user,
            'new_email': new_email,
            'verification_url': verification_url,
            'expiry_hours': 24,
        }

        # Render email template
        plain_message = render_to_string('accounts/emails/email_verification.txt', context)

        subject = 'QuietPage - Email Verification'
        from_email = settings.DEFAULT_FROM_EMAIL

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[new_email],
            fail_silently=False
        )

        logger.info(f"Verification email sent to {new_email} for user {user.username}")
        return True

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found, cannot send verification email")
        return False

    except Exception as e:
        logger.error(f"Failed to send verification email to {new_email}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, ignore_result=True)
def send_reminder_emails(self):
    """
    Send daily writing reminders to users who have enabled them.

    This task runs daily (scheduled via Celery Beat) and sends reminder
    emails to users based on their timezone and reminder_time preferences.

    Process:
    1. Find users with reminder_enabled=True
    2. Check if it's the right time in their timezone
    3. Check if they haven't written today
    4. Send personalized reminder email

    Returns:
        dict: {'sent': int, 'skipped': int, 'errors': int}
    """
    stats = {'sent': 0, 'skipped': 0, 'errors': 0}

    try:
        # Get users with reminders enabled
        users_with_reminders = User.objects.filter(
            reminder_enabled=True,
            email_notifications=True,  # Respect email notification preference
            is_active=True
        )

        logger.info(f"Processing reminders for {users_with_reminders.count()} users")

        for user in users_with_reminders:
            try:
                # Get current time in user's timezone
                user_tz = user.timezone
                now_in_user_tz = timezone.now().astimezone(user_tz)
                current_time = now_in_user_tz.time()

                # Check if it's within 1 hour of user's reminder time
                reminder_time = user.reminder_time or time(8, 0)
                time_diff = abs(
                    (current_time.hour * 60 + current_time.minute) -
                    (reminder_time.hour * 60 + reminder_time.minute)
                )

                # Skip if not within reminder window (1 hour)
                if time_diff > 60:
                    stats['skipped'] += 1
                    continue

                # Check if user has already written today
                today_in_user_tz = now_in_user_tz.date()
                has_written_today = (
                    user.last_entry_date and
                    user.last_entry_date >= today_in_user_tz
                )

                if has_written_today:
                    stats['skipped'] += 1
                    continue

                # Send reminder email
                context = {
                    'user': user,
                    'dashboard_url': f"{settings.SITE_URL}/",
                    'settings_url': f"{settings.SITE_URL}/settings",
                }

                plain_message = render_to_string('accounts/emails/reminder.txt', context)

                send_mail(
                    subject='QuietPage - Time to Write!',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False
                )

                stats['sent'] += 1
                logger.debug(f"Reminder sent to {user.username}")

            except Exception as e:
                logger.error(f"Failed to send reminder to user {user.id}: {e}")
                stats['errors'] += 1

        logger.info(f"Reminder emails complete: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Reminder email task failed: {e}", exc_info=True)
        return stats
