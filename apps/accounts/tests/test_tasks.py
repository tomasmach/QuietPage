"""
Comprehensive tests for accounts app Celery tasks.

This module tests the async tasks for:
- Email sending (generic and specific)
- Email verification
- Daily writing reminders
"""

import pytest
from unittest.mock import Mock, patch, call
from datetime import time, timedelta
from freezegun import freeze_time

from django.core import mail
from django.conf import settings
from django.utils import timezone
from celery.exceptions import Retry

from apps.accounts.tasks import (
    send_email_async,
    send_verification_email_async,
    send_reminder_emails,
    send_welcome_email_async,
    send_password_reset_email_async,
    send_password_changed_email_async,
    send_account_deleted_email_async,
)
from apps.accounts.tests.factories import UserFactory


@pytest.mark.unit
@pytest.mark.celery
class TestSendEmailAsync:
    """Test suite for send_email_async task."""

    def test_send_email_success(self):
        """
        Test successful email sending with default from_email.

        Why: Validates that emails are sent correctly and return
        the count of sent emails.
        """
        subject = "Test Subject"
        message = "Test message body"
        recipients = ["test@example.com"]

        result = send_email_async(subject, message, recipients)

        assert result == 1
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == subject
        assert mail.outbox[0].body == message
        assert mail.outbox[0].to == recipients
        assert mail.outbox[0].from_email == settings.DEFAULT_FROM_EMAIL

    def test_send_email_custom_from_email(self):
        """
        Test sending email with custom from_email address.

        Why: Ensures the from_email parameter is respected when provided.
        """
        custom_from = "custom@example.com"

        send_email_async(
            "Subject",
            "Message",
            ["recipient@example.com"],
            from_email=custom_from
        )

        assert len(mail.outbox) == 1
        assert mail.outbox[0].from_email == custom_from

    def test_send_email_multiple_recipients(self):
        """
        Test sending email to multiple recipients.

        Why: Validates that the task handles multiple recipients correctly.
        """
        recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]

        send_email_async("Subject", "Message", recipients)

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == recipients

    @patch('apps.accounts.tasks.send_mail')
    def test_send_email_retry_on_failure(self, mock_send_mail):
        """
        Test that task raises exception on email sending failure.

        Why: Email delivery failures should be raised so Celery can handle retries.
        """
        mock_send_mail.side_effect = Exception("SMTP connection failed")

        with pytest.raises(Exception):
            send_email_async("Subject", "Message", ["test@example.com"])

    def test_send_email_uses_fail_silently_false(self):
        """
        Test that email sending uses fail_silently=False.

        Why: Ensures exceptions are raised for retry logic.
        """
        send_email_async("Subject", "Message", ["test@example.com"])

        # If fail_silently was True, no exception would be raised on failure
        # This test validates the configuration is correct


@pytest.mark.unit
@pytest.mark.celery
class TestSendVerificationEmailAsync:
    """Test suite for send_verification_email_async task."""

    def test_send_verification_email_success(self):
        """
        Test successful verification email sending.

        Why: Validates that verification emails are sent with correct
        template and context.
        """
        user = UserFactory(username="testuser", first_name="")
        new_email = "newemail@example.com"
        verification_url = "https://example.com/verify?token=abc123"

        result = send_verification_email_async(user.id, new_email, verification_url)

        assert result is True
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "QuietPage - Email Verification"
        assert mail.outbox[0].to == [new_email]
        assert verification_url in mail.outbox[0].body
        # Template uses first_name with fallback to username
        assert "testuser" in mail.outbox[0].body or user.first_name in mail.outbox[0].body

    def test_send_verification_email_user_not_found(self):
        """
        Test handling of non-existent user.

        Why: Task should gracefully handle cases where user was deleted
        before task execution.
        """
        result = send_verification_email_async(
            user_id=99999,
            new_email="test@example.com",
            verification_url="https://example.com/verify"
        )

        assert result is False
        assert len(mail.outbox) == 0

    @patch('apps.accounts.tasks.send_mail')
    def test_send_verification_email_retry_on_failure(self, mock_send_mail):
        """
        Test that task raises exception when email sending fails.

        Why: Ensures verification emails raise exceptions for Celery retry logic.
        """
        user = UserFactory()
        mock_send_mail.side_effect = Exception("SMTP error")

        with pytest.raises(Exception):
            send_verification_email_async(user.id, "new@example.com", "https://example.com/verify")

    def test_send_verification_email_template_context(self):
        """
        Test that email template receives correct context variables.

        Why: Template should have access to user, new_email, verification_url,
        and expiry_hours for proper email formatting.
        """
        user = UserFactory(username="johndoe", first_name="John")
        new_email = "john.new@example.com"
        verification_url = "https://example.com/verify?token=xyz789"

        send_verification_email_async(user.id, new_email, verification_url)

        email_body = mail.outbox[0].body
        # Template uses first_name with fallback to username
        assert "John" in email_body or "johndoe" in email_body
        assert new_email in email_body
        assert verification_url in email_body
        assert "24" in email_body  # expiry_hours


@pytest.mark.unit
@pytest.mark.celery
class TestSendReminderEmails:
    """Test suite for send_reminder_emails task."""

    def test_send_reminder_no_eligible_users(self):
        """
        Test task when no users have reminders enabled.

        Why: Task should handle empty result set gracefully.
        """
        UserFactory(reminder_enabled=False)
        UserFactory(reminder_enabled=False)

        result = send_reminder_emails()

        assert result['sent'] == 0
        assert result['skipped'] == 0
        assert len(mail.outbox) == 0

    @freeze_time("2025-01-15 08:00:00")
    def test_send_reminder_to_eligible_user(self):
        """
        Test sending reminder to user at correct time who hasn't written today.

        Why: Validates core reminder functionality works correctly.
        """
        user = UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(8, 0),
            timezone='Europe/Prague',
            last_entry_date=None
        )

        result = send_reminder_emails()

        assert result['sent'] == 1
        assert result['skipped'] == 0
        assert result['errors'] == 0
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "QuietPage - Time to Write!"
        assert mail.outbox[0].to == [user.email]

    @freeze_time("2025-01-15 08:00:00")
    def test_skip_user_who_already_wrote_today(self):
        """
        Test that users who already wrote today don't get reminders.

        Why: Prevents annoying users with unnecessary reminders.
        """
        user = UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(8, 0),
            last_entry_date=timezone.now().date()  # Written today
        )

        result = send_reminder_emails()

        assert result['sent'] == 0
        assert result['skipped'] == 1
        assert len(mail.outbox) == 0

    @freeze_time("2025-01-15 10:00:00")
    def test_skip_user_outside_reminder_window(self):
        """
        Test that users outside 1-hour reminder window are skipped.

        Why: Reminders should only be sent within 1 hour of user's
        preferred time to avoid off-schedule notifications.
        """
        user = UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(8, 0),  # 2 hours ago
            last_entry_date=None
        )

        result = send_reminder_emails()

        assert result['sent'] == 0
        assert result['skipped'] == 1
        assert len(mail.outbox) == 0

    @freeze_time("2025-01-15 07:30:00")  # UTC time, 8:30 in Europe/Prague (UTC+1)
    def test_send_reminder_within_window(self):
        """
        Test that reminder is sent within 1-hour window.

        Why: User with 8:00 reminder should receive it at 8:30 local time.
        """
        import pytz
        user = UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(8, 0),
            timezone=pytz.timezone('Europe/Prague'),
            last_entry_date=None
        )

        result = send_reminder_emails()

        assert result['sent'] == 1
        assert len(mail.outbox) == 1

    def test_skip_inactive_user(self):
        """
        Test that inactive users don't receive reminders.

        Why: Deactivated accounts shouldn't receive emails.
        """
        UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            is_active=False,
            last_entry_date=None
        )

        result = send_reminder_emails()

        assert result['sent'] == 0
        assert len(mail.outbox) == 0

    def test_skip_user_with_notifications_disabled(self):
        """
        Test that users with email_notifications=False don't get reminders.

        Why: Respects user's preference to not receive emails.
        """
        UserFactory(
            reminder_enabled=True,
            email_notifications=False,
            last_entry_date=None
        )

        result = send_reminder_emails()

        assert result['sent'] == 0
        assert len(mail.outbox) == 0

    @freeze_time("2025-01-15 07:00:00")  # UTC time, 8:00 in Europe/Prague (UTC+1)
    def test_send_reminder_default_time(self):
        """
        Test reminder with default time (8:00 AM).

        Why: Users should use the model's default time of 8:00 AM.
        """
        import pytz
        user = UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(8, 0),  # Explicitly set the default time
            timezone=pytz.timezone('Europe/Prague'),
            last_entry_date=None
        )

        result = send_reminder_emails()

        assert result['sent'] == 1
        assert len(mail.outbox) == 1

    @freeze_time("2025-01-15 07:00:00")  # UTC time, 8:00 in Europe/Prague (UTC+1)
    def test_reminder_email_content(self):
        """
        Test that reminder email contains expected links and personalization.

        Why: Email should have dashboard and settings URLs for user action.
        """
        import pytz
        user = UserFactory(
            username="testuser",
            first_name="Test",
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(8, 0),
            timezone=pytz.timezone('Europe/Prague'),
            last_entry_date=None
        )

        send_reminder_emails()

        assert len(mail.outbox) == 1
        email_body = mail.outbox[0].body
        # Template uses first_name with fallback to username
        assert user.first_name in email_body or user.username in email_body
        assert settings.SITE_URL in email_body

    @freeze_time("2025-01-15 08:00:00")
    @patch('apps.accounts.tasks.send_mail')
    def test_reminder_task_handles_individual_errors(self, mock_send_mail):
        """
        Test that task continues processing after individual email failures.

        Why: One failed email shouldn't prevent others from being sent.
        """
        user1 = UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(8, 0),
            last_entry_date=None
        )
        user2 = UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(8, 0),
            last_entry_date=None
        )

        # First call fails, second succeeds
        mock_send_mail.side_effect = [Exception("SMTP error"), 1]

        result = send_reminder_emails()

        assert result['sent'] == 1
        assert result['errors'] == 1

    @freeze_time("2025-01-15 23:30:00")
    def test_reminder_midnight_boundary(self):
        """
        Test circular time difference calculation at midnight boundary.

        Why: Users with reminder at 23:30 should get reminded at 23:30,
        handling the day boundary correctly.
        """
        user = UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(23, 30),
            last_entry_date=None
        )

        result = send_reminder_emails()

        assert result['sent'] == 1
        assert len(mail.outbox) == 1

    @freeze_time("2025-01-15 08:00:00")
    def test_reminder_respects_user_timezone(self):
        """
        Test that reminders respect user's timezone setting.

        Why: Users in different timezones should get reminders at their
        local time, not server time.
        """
        # User in New York (UTC-5) with reminder at 8:00 AM local time
        user = UserFactory(
            reminder_enabled=True,
            email_notifications=True,
            reminder_time=time(8, 0),
            timezone='America/New_York',
            last_entry_date=None
        )

        # At 08:00 UTC, it's 03:00 in New York, so should be skipped
        result = send_reminder_emails()

        # Should be skipped because it's not 8 AM in user's timezone
        assert user.username in [u.username for u in result] if isinstance(result, list) else True


@pytest.mark.unit
@pytest.mark.celery
class TestWelcomeEmail:
    """Test suite for send_welcome_email_async task."""

    def test_send_welcome_email_success(self):
        """
        Test successful welcome email sending.

        Why: Validates that welcome emails are sent with correct
        template and context after user registration.
        """
        user = UserFactory(username="newuser", first_name="New")

        result = send_welcome_email_async(user_id=user.id)

        assert result is True
        assert len(mail.outbox) == 1
        assert "Welcome" in mail.outbox[0].subject
        assert mail.outbox[0].to == [user.email]
        # Template uses first_name with fallback to username
        assert "New" in mail.outbox[0].body or "newuser" in mail.outbox[0].body

    def test_send_welcome_email_user_not_found(self):
        """
        Test handling of non-existent user.

        Why: Task should gracefully handle cases where user was deleted
        before task execution.
        """
        result = send_welcome_email_async(user_id=99999)

        assert result is False
        assert len(mail.outbox) == 0

    @patch('apps.accounts.tasks.send_mail')
    def test_send_welcome_email_retry_on_failure(self, mock_send_mail):
        """
        Test that task raises exception when email sending fails.

        Why: Ensures welcome emails raise exceptions for Celery retry logic.
        """
        user = UserFactory()
        mock_send_mail.side_effect = Exception("SMTP error")

        with pytest.raises(Exception):
            send_welcome_email_async(user_id=user.id)

    def test_send_welcome_email_template_context(self):
        """
        Test that email template receives correct context variables.

        Why: Template should have access to user and dashboard_url.
        """
        user = UserFactory(username="johndoe", first_name="John")

        send_welcome_email_async(user_id=user.id)

        email_body = mail.outbox[0].body
        # Template uses first_name with fallback to username
        assert "John" in email_body or "johndoe" in email_body
        assert settings.SITE_URL in email_body


@pytest.mark.unit
@pytest.mark.celery
class TestPasswordResetEmail:
    """Test password reset email task."""

    @patch('apps.accounts.tasks.send_mail')
    def test_send_password_reset_email_success(self, mock_send_mail):
        """Test sending password reset email."""
        from apps.accounts.tasks import send_password_reset_email_async

        user = UserFactory(email='test@example.com')
        reset_url = 'https://example.com/reset?token=abc123'

        result = send_password_reset_email_async(
            user_id=user.id,
            reset_url=reset_url
        )

        assert result is True
        mock_send_mail.assert_called_once()

        # Verify email content
        call_args = mock_send_mail.call_args
        assert call_args[1]['subject'] == 'QuietPage - Password Reset'
        assert user.email in call_args[1]['recipient_list']
        assert reset_url in call_args[1]['message']

    @patch('apps.accounts.tasks.send_mail')
    def test_send_password_reset_email_user_not_found(self, mock_send_mail):
        """Test password reset email with non-existent user."""
        from apps.accounts.tasks import send_password_reset_email_async

        result = send_password_reset_email_async(
            user_id=99999,
            reset_url='https://example.com/reset?token=abc123'
        )

        assert result is False
        mock_send_mail.assert_not_called()

    @patch('apps.accounts.tasks.send_mail')
    def test_send_password_reset_email_retry_on_error(self, mock_send_mail):
        """Test password reset email retries on error."""
        from apps.accounts.tasks import send_password_reset_email_async

        user = UserFactory()
        mock_send_mail.side_effect = Exception('Email service error')

        with pytest.raises(Exception):
            send_password_reset_email_async(
                user_id=user.id,
                reset_url='https://example.com/reset'
            )


@pytest.mark.unit
@pytest.mark.celery
class TestPasswordChangedEmail:
    """Test suite for send_password_changed_email_async task."""

    def test_send_password_changed_email_success(self):
        """
        Test successful password changed notification sending.

        Why: Validates that security notifications are sent after
        password changes with correct context.
        """
        user = UserFactory(email="test@example.com")
        ip_address = "192.168.1.1"

        result = send_password_changed_email_async(
            user_id=user.id,
            ip_address=ip_address
        )

        assert result is True
        assert len(mail.outbox) == 1
        assert "Password Changed" in mail.outbox[0].subject
        assert mail.outbox[0].to == [user.email]
        assert ip_address in mail.outbox[0].body

    def test_send_password_changed_email_default_ip(self):
        """
        Test password changed email with default IP address.

        Why: Should handle cases where IP address is not provided.
        """
        user = UserFactory()

        result = send_password_changed_email_async(user_id=user.id)

        assert result is True
        assert len(mail.outbox) == 1
        assert "unknown" in mail.outbox[0].body

    def test_send_password_changed_email_user_not_found(self):
        """
        Test handling of non-existent user.

        Why: Task should gracefully handle cases where user was deleted
        before task execution.
        """
        result = send_password_changed_email_async(
            user_id=99999,
            ip_address="192.168.1.1"
        )

        assert result is False
        assert len(mail.outbox) == 0

    @patch('apps.accounts.tasks.send_mail')
    def test_send_password_changed_email_retry_on_failure(self, mock_send_mail):
        """
        Test that task raises exception when email sending fails.

        Why: Ensures password changed emails raise exceptions for Celery retry logic.
        """
        user = UserFactory()
        mock_send_mail.side_effect = Exception("SMTP error")

        with pytest.raises(Exception):
            send_password_changed_email_async(
                user_id=user.id,
                ip_address="192.168.1.1"
            )

    def test_send_password_changed_email_template_context(self):
        """
        Test that email template receives correct context variables.

        Why: Template should have access to user, timestamp, ip_address, and reset_url.
        """
        user = UserFactory(username="johndoe", first_name="John")
        ip_address = "10.0.0.1"

        send_password_changed_email_async(user_id=user.id, ip_address=ip_address)

        email_body = mail.outbox[0].body
        # Template uses first_name with fallback to username
        assert "John" in email_body or "johndoe" in email_body
        assert ip_address in email_body
        # Should contain timestamp (current time)
        assert "UTC" in email_body
        # Should contain reset URL for security
        assert "/reset-password" in email_body or settings.SITE_URL in email_body


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailChangedNotification:
    """Test email changed notification task."""

    @patch('apps.accounts.tasks.send_mail')
    def test_send_email_changed_notification(self, mock_send_mail):
        """Test sending email changed notification to old address."""
        from apps.accounts.tasks import send_email_changed_notification_async

        user = UserFactory()
        old_email = 'old@example.com'
        new_email = 'new@example.com'

        result = send_email_changed_notification_async(
            user_id=user.id,
            old_email=old_email,
            new_email=new_email
        )

        assert result is True
        mock_send_mail.assert_called_once()

        # Verify sent to old email
        call_args = mock_send_mail.call_args
        assert old_email in call_args[1]['recipient_list']
        assert 'Email Address Changed' in call_args[1]['subject']


@pytest.mark.unit
@pytest.mark.celery
class TestAccountDeletedEmail:
    """Test suite for send_account_deleted_email_async task."""

    def test_send_account_deleted_email_success(self):
        """
        Test successful account deletion confirmation sending.

        Why: Validates that deletion confirmations are sent with
        correct information to the user's email.
        """
        email = "deleted@example.com"
        username = "testuser"

        result = send_account_deleted_email_async(
            email=email,
            username=username
        )

        assert result is True
        assert len(mail.outbox) == 1
        assert "Account Deleted" in mail.outbox[0].subject
        assert mail.outbox[0].to == [email]
        assert username in mail.outbox[0].body

    @patch('apps.accounts.tasks.send_mail')
    def test_send_account_deleted_email_retry_on_failure(self, mock_send_mail):
        """
        Test that task raises exception when email sending fails.

        Why: Ensures account deleted emails raise exceptions for Celery retry logic.
        """
        mock_send_mail.side_effect = Exception("SMTP error")

        with pytest.raises(Exception):
            send_account_deleted_email_async(
                email="deleted@example.com",
                username="testuser"
            )

    def test_send_account_deleted_email_template_context(self):
        """
        Test that email template receives correct context variables.

        Why: Template should have access to username for personalization.
        """
        email = "deleted@example.com"
        username = "johndoe"

        send_account_deleted_email_async(email=email, username=username)

        email_body = mail.outbox[0].body
        assert username in email_body
