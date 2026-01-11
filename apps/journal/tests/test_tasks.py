"""
Comprehensive tests for journal app Celery tasks.

This module tests the async tasks for:
- Email change request cleanup
- Weekly data cleanup
- User data export (GDPR compliance)
- Daily statistics aggregation
"""

import pytest
import json
from unittest.mock import Mock, patch, call
from datetime import timedelta
from freezegun import freeze_time

from django.utils import timezone
from celery.exceptions import Retry

from apps.journal.tasks import (
    cleanup_expired_email_requests,
    weekly_cleanup,
    export_user_data,
    aggregate_daily_statistics,
)
from apps.accounts.models import EmailChangeRequest
from apps.accounts.tests.factories import UserFactory, EmailChangeRequestFactory
from apps.journal.tests.factories import EntryFactory


def generate_content_with_words(count):
    """Generate content with exact word count for testing."""
    return ' '.join(['word'] * count)


@pytest.mark.unit
@pytest.mark.celery
class TestCleanupExpiredEmailRequests:
    """Test suite for cleanup_expired_email_requests task."""

    def test_cleanup_expired_requests_success(self):
        """
        Test successful cleanup of expired email change requests.

        Why: Expired requests should be removed to keep database clean.
        """
        user = UserFactory()

        # Create expired request
        expired_request = EmailChangeRequestFactory(
            user=user,
            is_verified=False,
            expires_at=timezone.now() - timedelta(hours=1)
        )

        # Create valid request (should not be deleted)
        valid_request = EmailChangeRequestFactory(
            user=user,
            is_verified=False,
            expires_at=timezone.now() + timedelta(hours=1)
        )

        result = cleanup_expired_email_requests()

        assert result['deleted'] == 1
        assert result['errors'] == 0
        assert not EmailChangeRequest.objects.filter(pk=expired_request.pk).exists()
        assert EmailChangeRequest.objects.filter(pk=valid_request.pk).exists()

    def test_cleanup_skips_verified_requests(self):
        """
        Test that verified requests are not deleted even if expired.

        Why: Verified requests should be kept for audit trail.
        """
        user = UserFactory()

        verified_request = EmailChangeRequestFactory(
            user=user,
            is_verified=True,
            verified_at=timezone.now(),
            expires_at=timezone.now() - timedelta(hours=1)
        )

        result = cleanup_expired_email_requests()

        assert result['deleted'] == 0
        assert EmailChangeRequest.objects.filter(pk=verified_request.pk).exists()

    def test_cleanup_no_expired_requests(self):
        """
        Test cleanup when no expired requests exist.

        Why: Task should handle empty result set gracefully.
        """
        user = UserFactory()

        EmailChangeRequestFactory(
            user=user,
            is_verified=False,
            expires_at=timezone.now() + timedelta(hours=24)
        )

        result = cleanup_expired_email_requests()

        assert result['deleted'] == 0
        assert result['errors'] == 0

    def test_cleanup_multiple_expired_requests(self):
        """
        Test cleanup of multiple expired requests.

        Why: Bulk cleanup should work correctly.
        """
        user = UserFactory()

        for _ in range(5):
            EmailChangeRequestFactory(
                user=user,
                is_verified=False,
                expires_at=timezone.now() - timedelta(hours=1)
            )

        result = cleanup_expired_email_requests()

        assert result['deleted'] == 5
        assert EmailChangeRequest.objects.filter(
            user=user,
            is_verified=False
        ).count() == 0

    def test_cleanup_handles_exceptions(self):
        """
        Test that cleanup handles database errors gracefully.

        Why: Task should not crash on database errors.
        """
        with patch('apps.journal.tasks.EmailChangeRequest.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")

            result = cleanup_expired_email_requests()

        assert result['deleted'] == 0
        assert result['errors'] == 1


@pytest.mark.unit
@pytest.mark.celery
class TestWeeklyCleanup:
    """Test suite for weekly_cleanup task."""

    @freeze_time("2025-01-15 03:00:00")
    def test_weekly_cleanup_old_requests(self):
        """
        Test cleanup of very old email change requests (>30 days).

        Why: Old unverified requests should be removed even if not expired.
        """
        user = UserFactory()

        # Create old request (created 35 days ago)
        old_time = timezone.now() - timedelta(days=35)
        with freeze_time(old_time):
            old_request = EmailChangeRequestFactory(
                user=user,
                is_verified=False
            )

        # Create recent request (created 10 days ago)
        recent_time = timezone.now() - timedelta(days=10)
        with freeze_time(recent_time):
            recent_request = EmailChangeRequestFactory(
                user=user,
                is_verified=False
            )

        result = weekly_cleanup()

        assert result['old_email_requests_deleted'] == 1
        assert result['errors'] == 0
        assert not EmailChangeRequest.objects.filter(pk=old_request.pk).exists()
        assert EmailChangeRequest.objects.filter(pk=recent_request.pk).exists()

    @freeze_time("2025-01-15 03:00:00")
    def test_weekly_cleanup_no_old_requests(self):
        """
        Test weekly cleanup when no old requests exist.

        Why: Task should handle empty result set gracefully.
        """
        user = UserFactory()

        EmailChangeRequestFactory(
            user=user,
            is_verified=False
        )

        result = weekly_cleanup()

        assert result['old_email_requests_deleted'] == 0
        assert result['errors'] == 0

    @freeze_time("2025-01-15 03:00:00")
    def test_weekly_cleanup_keeps_verified_requests(self):
        """
        Test that verified requests are kept even if old.

        Why: Verified requests should be preserved for audit purposes.
        """
        user = UserFactory()

        old_time = timezone.now() - timedelta(days=35)
        with freeze_time(old_time):
            verified_request = EmailChangeRequestFactory(
                user=user,
                is_verified=True,
                verified_at=old_time
            )

        result = weekly_cleanup()

        assert result['old_email_requests_deleted'] == 0
        assert EmailChangeRequest.objects.filter(pk=verified_request.pk).exists()

    def test_weekly_cleanup_handles_exceptions(self):
        """
        Test that weekly cleanup handles errors gracefully.

        Why: Task should complete even if cleanup fails.
        """
        with patch('apps.journal.tasks.EmailChangeRequest.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")

            result = weekly_cleanup()

        assert result['errors'] == 1


@pytest.mark.unit
@pytest.mark.celery
class TestExportUserData:
    """Test suite for export_user_data task."""

    @patch('apps.journal.tasks.send_export_link_email')
    @patch('apps.journal.tasks.upload_export_to_secure_storage')
    def test_export_user_data_success(self, mock_upload, mock_send_email):
        """
        Test successful user data export.

        Why: Validates GDPR data export functionality works correctly.
        """
        user = UserFactory(
            username="testuser",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            bio="Test bio",
            daily_word_goal=1000,
        )

        # Create entries for the user
        entry1 = EntryFactory(
            user=user,
            title="Entry 1",
            content="Content 1",
            word_count=100,
            mood_rating=4,
            is_favorite=True
        )
        entry2 = EntryFactory(
            user=user,
            title="Entry 2",
            content="Content 2",
            word_count=200,
            mood_rating=5,
            is_favorite=False
        )

        # Set streak values after entries are created to avoid signal recalculation
        user.current_streak = 5
        user.longest_streak = 10
        user.save()

        mock_upload.return_value = "/path/to/export.json"

        result = export_user_data(user.id)

        # Verify upload was called with correct data structure
        assert mock_upload.call_count == 1
        upload_args = mock_upload.call_args[0]
        assert upload_args[0] == user.id
        user_data = upload_args[1]

        # Verify user data structure
        assert user_data['user']['username'] == "testuser"
        assert user_data['user']['email'] == "test@example.com"
        assert user_data['preferences']['daily_word_goal'] == 1000
        assert user_data['statistics']['current_streak'] == 5
        assert user_data['statistics']['longest_streak'] == 10
        assert len(user_data['entries']) == 2

        # Verify email was sent
        mock_send_email.assert_called_once_with(
            "test@example.com",
            "testuser",
            "/path/to/export.json"
        )

    @patch('apps.journal.tasks.send_export_link_email')
    @patch('apps.journal.tasks.upload_export_to_secure_storage')
    def test_export_includes_all_entries(self, mock_upload, mock_send_email):
        """
        Test that export includes all user entries.

        Why: Complete data export is required for GDPR compliance.
        """
        user = UserFactory()

        # Create entries with explicit content
        entries = EntryFactory.create_batch(
            10,
            user=user,
            content="test content"
        )

        # Verify setup
        assert user.journal_entries.count() == 10, "Setup failed"

        mock_upload.return_value = "/path/to/export.json"

        export_user_data(user.id)

        user_data = mock_upload.call_args[0][1]
        assert len(user_data['entries']) == 10

    @patch('apps.journal.tasks.send_export_link_email')
    @patch('apps.journal.tasks.upload_export_to_secure_storage')
    def test_export_decrypts_content(self, mock_upload, mock_send_email):
        """
        Test that exported content is decrypted.

        Why: User should receive readable content, not encrypted data.
        """
        user = UserFactory()
        entry = EntryFactory(
            user=user,
            title="Test Entry",
            content="This is secret content that should be decrypted"
        )

        mock_upload.return_value = "/path/to/export.json"

        export_user_data(user.id)

        user_data = mock_upload.call_args[0][1]
        exported_entry = user_data['entries'][0]

        # Content should be decrypted (EncryptedTextField auto-decrypts)
        assert exported_entry['content'] == "This is secret content that should be decrypted"

    def test_export_user_not_found(self):
        """
        Test export when user doesn't exist.

        Why: Task should handle deleted users gracefully.
        """
        result = export_user_data(user_id=99999)

        assert result is None

    @patch('apps.journal.tasks.upload_export_to_secure_storage')
    def test_export_retry_on_failure(self, mock_upload):
        """
        Test that task retries on export failure.

        Why: Transient failures should not prevent data export.
        """
        user = UserFactory()
        mock_upload.side_effect = Exception("Storage unavailable")

        with pytest.raises(Exception):
            export_user_data(user.id)

    @patch('apps.journal.tasks.send_export_link_email')
    @patch('apps.journal.tasks.upload_export_to_secure_storage')
    def test_export_includes_timestamp(self, mock_upload, mock_send_email):
        """
        Test that export includes timestamp.

        Why: Users should know when export was generated.
        """
        user = UserFactory()
        mock_upload.return_value = "/path/to/export.json"

        with freeze_time("2025-01-15 14:30:00"):
            export_user_data(user.id)

        user_data = mock_upload.call_args[0][1]
        assert 'export_timestamp' in user_data
        assert user_data['export_timestamp'] == "2025-01-15T14:30:00+00:00"

    @patch('apps.journal.tasks.send_export_link_email')
    @patch('apps.journal.tasks.upload_export_to_secure_storage')
    def test_export_includes_tags(self, mock_upload, mock_send_email):
        """
        Test that exported entries include tags.

        Why: Complete data export must include all entry metadata.
        """
        user = UserFactory()
        entry = EntryFactory(user=user)

        # Add tags to entry
        entry.tags.add("work", "personal")

        mock_upload.return_value = "/path/to/export.json"

        export_user_data(user.id)

        user_data = mock_upload.call_args[0][1]
        exported_entry = user_data['entries'][0]

        assert set(exported_entry['tags']) == {"work", "personal"}

    @patch('apps.journal.tasks.send_export_link_email')
    @patch('apps.journal.tasks.upload_export_to_secure_storage')
    def test_export_entries_ordered_by_created_at(self, mock_upload, mock_send_email):
        """
        Test that entries are exported in chronological order.

        Why: Chronological ordering makes export more useful.
        """
        user = UserFactory()

        with freeze_time("2025-01-10"):
            entry1 = EntryFactory(user=user, title="First")

        with freeze_time("2025-01-12"):
            entry2 = EntryFactory(user=user, title="Second")

        with freeze_time("2025-01-11"):
            entry3 = EntryFactory(user=user, title="Third")

        mock_upload.return_value = "/path/to/export.json"

        export_user_data(user.id)

        user_data = mock_upload.call_args[0][1]
        titles = [e['title'] for e in user_data['entries']]

        assert titles == ["First", "Third", "Second"]


@pytest.mark.unit
@pytest.mark.celery
class TestAggregateDailyStatistics:
    """Test suite for aggregate_daily_statistics task."""

    def test_aggregate_statistics_success(self):
        """
        Test successful statistics aggregation.

        Why: Validates basic stats calculation works correctly.
        """
        user = UserFactory(
            current_streak=5,
            longest_streak=10
        )

        # Create entries with exact word counts
        EntryFactory.create_batch(
            3,
            user=user,
            content=generate_content_with_words(500),
            is_favorite=False
        )
        EntryFactory(
            user=user,
            content=generate_content_with_words(300),
            is_favorite=True
        )
        EntryFactory(
            user=user,
            content=generate_content_with_words(200),
            is_favorite=True
        )

        # Refresh user to get updated streak values from signals
        user.refresh_from_db()

        result = aggregate_daily_statistics(user.id)

        assert result['total_entries'] == 5
        assert result['total_words'] == 2000
        assert result['favorite_entries'] == 2
        assert result['current_streak'] == user.current_streak
        assert result['longest_streak'] == user.longest_streak

    def test_aggregate_statistics_no_entries(self):
        """
        Test statistics for user with no entries.

        Why: Should handle new users with zero entries.
        """
        user = UserFactory(current_streak=0, longest_streak=0)

        result = aggregate_daily_statistics(user.id)

        assert result['total_entries'] == 0
        assert result['total_words'] == 0
        assert result['favorite_entries'] == 0

    def test_aggregate_statistics_user_not_found(self):
        """
        Test aggregation when user doesn't exist.

        Why: Should handle deleted users gracefully.
        """
        result = aggregate_daily_statistics(user_id=99999)

        assert result is None

    def test_aggregate_statistics_handles_exceptions(self):
        """
        Test that aggregation handles errors gracefully.

        Why: Task should not crash on database errors.
        """
        user = UserFactory()

        with patch('apps.journal.tasks.Entry.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")

            result = aggregate_daily_statistics(user.id)

        assert result is None
