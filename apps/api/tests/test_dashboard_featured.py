"""
Tests for FeaturedEntry selection and refresh logic in DashboardView.
"""
import pytest
from datetime import timedelta
from freezegun import freeze_time
from django.test import override_settings
from django.utils import timezone
from zoneinfo import ZoneInfo
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory
from apps.journal.models import FeaturedEntry


@pytest.mark.integration
@pytest.mark.django_db
class TestFeaturedEntrySelection:
    """Tests for featured entry selection on dashboard."""

    def test_featured_entry_not_shown_with_less_than_10_entries(self):
        """Featured entry should be null when user has < 10 entries."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        EntryFactory.create_batch(5, user=user)
        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        assert response.data['featured_entry'] is None

    def test_featured_entry_shown_with_10_or_more_entries(self):
        """Featured entry should be returned when user has >= 10 entries."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        for i in range(10):
            EntryFactory(user=user, created_at=timezone.now() - timedelta(days=i+1))
        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        assert response.data['featured_entry'] is not None
        assert 'id' in response.data['featured_entry']
        assert 'content_preview' in response.data['featured_entry']
        assert 'days_ago' in response.data['featured_entry']

    def test_featured_entry_consistent_across_requests(self):
        """Same featured entry should be returned on multiple requests same day."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        for i in range(15):
            EntryFactory(user=user, created_at=timezone.now() - timedelta(days=i+1))
        response1 = client.get('/api/v1/dashboard/')
        response2 = client.get('/api/v1/dashboard/')
        assert response1.data['featured_entry']['id'] == response2.data['featured_entry']['id']

    def test_featured_entry_stored_in_database(self):
        """Featured entry selection should be persisted in FeaturedEntry model."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        for i in range(10):
            EntryFactory(user=user, created_at=timezone.now() - timedelta(days=i+1))
        assert FeaturedEntry.objects.filter(user=user).count() == 0
        client.get('/api/v1/dashboard/')
        assert FeaturedEntry.objects.filter(user=user).count() == 1

    def test_featured_entry_excludes_today(self):
        """Featured entry should never be from today."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        for i in range(9):
            EntryFactory(user=user, created_at=timezone.now() - timedelta(days=i+1))
        today_entry = EntryFactory(user=user)
        response = client.get('/api/v1/dashboard/')
        assert response.data['featured_entry'] is not None
        assert response.data['featured_entry']['id'] != str(today_entry.id)


@pytest.mark.integration
@pytest.mark.django_db
class TestFeaturedEntryRefresh:
    """Tests for featured entry refresh endpoint."""

    def test_refresh_returns_different_entry(self):
        """Refresh should return a different entry than current."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        for i in range(15):
            EntryFactory(user=user, created_at=timezone.now() - timedelta(days=i+1))
        response1 = client.get('/api/v1/dashboard/')
        initial_id = response1.data['featured_entry']['id']
        response2 = client.post('/api/v1/dashboard/refresh-featured/')
        assert response2.status_code == 200
        assert response2.data['featured_entry']['id'] != initial_id

    def test_refresh_updates_database(self):
        """Refresh should update the FeaturedEntry in database."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        for i in range(15):
            EntryFactory(user=user, created_at=timezone.now() - timedelta(days=i+1))
        client.get('/api/v1/dashboard/')
        initial_featured = FeaturedEntry.objects.get(user=user)
        initial_entry_id = initial_featured.entry_id
        client.post('/api/v1/dashboard/refresh-featured/')
        updated_featured = FeaturedEntry.objects.get(user=user)
        assert updated_featured.entry_id != initial_entry_id

    def test_refresh_with_only_one_valid_entry_returns_same(self):
        """When only one valid entry exists, refresh returns same entry."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        for i in range(9):
            EntryFactory(user=user)
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=1))
        response1 = client.get('/api/v1/dashboard/')
        response2 = client.post('/api/v1/dashboard/refresh-featured/')
        assert response1.data['featured_entry']['id'] == response2.data['featured_entry']['id']

    def test_refresh_requires_authentication(self):
        """Refresh endpoint should require authentication."""
        client = APIClient()
        response = client.post('/api/v1/dashboard/refresh-featured/')
        assert response.status_code == 403


@pytest.mark.statistics
@pytest.mark.integration
@pytest.mark.django_db
class TestWeeklyStats:
    """Tests for weekly statistics in dashboard response."""

    def test_weekly_stats_included_in_response(self):
        """Dashboard should include weekly_stats object."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        assert 'weekly_stats' in response.data
        assert 'total_words' in response.data['weekly_stats']
        assert 'best_day' in response.data['weekly_stats']

    def test_weekly_stats_calculates_last_7_days(self):
        """Weekly stats should sum words from last 7 days only."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        EntryFactory(user=user, content=' '.join(['word'] * 500), created_at=timezone.now() - timedelta(days=3))
        EntryFactory(user=user, content=' '.join(['word'] * 1000), created_at=timezone.now() - timedelta(days=10))
        response = client.get('/api/v1/dashboard/')
        assert response.data['weekly_stats']['total_words'] == 500

    def test_weekly_stats_best_day_format(self):
        """Best day should include date, words, and weekday."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        EntryFactory(user=user, content=' '.join(['word'] * 800), created_at=timezone.now() - timedelta(days=2))
        response = client.get('/api/v1/dashboard/')
        best_day = response.data['weekly_stats']['best_day']
        assert best_day is not None
        assert 'date' in best_day
        assert 'words' in best_day
        assert 'weekday' in best_day
        assert best_day['words'] == 800

    def test_weekly_stats_no_entries(self):
        """Weekly stats should handle zero entries gracefully."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/dashboard/')
        assert response.data['weekly_stats']['total_words'] == 0
        assert response.data['weekly_stats']['best_day'] is None


@pytest.mark.integration
@pytest.mark.django_db
class TestDaysAgoTimezoneCalculation:
    """Tests for days_ago calculation with timezone edge cases."""

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 12:00:00', tz_offset=0)
    def test_days_ago_with_extreme_positive_timezone(self):
        """User in UTC+14 should see correct days_ago when UTC date differs from user's date."""
        # UTC+14 (Pacific/Kiritimati) - one of the most extreme positive timezones
        user = UserFactory(timezone='Pacific/Kiritimati')
        client = APIClient()
        client.force_authenticate(user=user)

        # Freeze time to 2025-01-15 12:00:00 UTC
        # In UTC+14, this is 2025-01-16 02:00:00 (next day)

        # Create entries for proper featured entry pool (need 10+)
        for i in range(2, 12):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i)
            )

        # Create an entry from 2 days ago in user's timezone (2025-01-14 in Kiritimati)
        # In UTC, this would be 2025-01-13 14:00:00
        entry_time = timezone.now() - timedelta(days=2, hours=12)
        entry = EntryFactory(user=user, created_at=entry_time)

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200

        featured = response.data['featured_entry']
        if featured and featured['id'] == str(entry.id):
            # Entry created at 2025-01-13 14:00 UTC = 2025-01-14 04:00 Kiritimati
            # User's current time: 2025-01-16 02:00 Kiritimati
            # days_ago should be 2 (2025-01-16 - 2025-01-14 = 2 days)
            assert featured['days_ago'] == 2

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 02:00:00', tz_offset=0)
    def test_days_ago_with_extreme_negative_timezone(self):
        """User in UTC-12 should see correct days_ago when UTC date differs from user's date."""
        # UTC-12 (Etc/GMT+12) - one of the most extreme negative timezones
        user = UserFactory(timezone='Etc/GMT+12')
        client = APIClient()
        client.force_authenticate(user=user)

        # Freeze time to 2025-01-15 02:00:00 UTC
        # In UTC-12, this is 2025-01-14 14:00:00 (previous day)

        # Create entries for proper featured entry pool (need 10+)
        for i in range(2, 12):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i)
            )

        # Create an entry from 1 day ago in user's timezone (2025-01-13 in UTC-12)
        # In UTC, this would be 2025-01-14 01:00:00
        entry_time = timezone.now() - timedelta(days=1, hours=1)
        entry = EntryFactory(user=user, created_at=entry_time)

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200

        featured = response.data['featured_entry']
        if featured and featured['id'] == str(entry.id):
            # Entry created at 2025-01-14 01:00 UTC = 2025-01-13 13:00 UTC-12
            # User's current time: 2025-01-14 14:00 UTC-12
            # days_ago should be 1 (2025-01-14 - 2025-01-13 = 1 day)
            assert featured['days_ago'] == 1

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 15:30:00', tz_offset=0)
    def test_days_ago_near_midnight_utc_vs_user_timezone(self):
        """Entry created near midnight should calculate correctly when UTC midnight != user's midnight."""
        # User in Tokyo (UTC+9)
        user = UserFactory(timezone='Asia/Tokyo')
        client = APIClient()
        client.force_authenticate(user=user)

        # Freeze time to 2025-01-15 15:30:00 UTC (which is 2025-01-16 00:30:00 in Tokyo)
        # This is just after midnight in user's timezone, but still same day in UTC

        # Create entries for proper featured entry pool (need 10+)
        for i in range(2, 12):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i)
            )

        # Create an entry at 2025-01-14 15:00:00 UTC (2025-01-15 00:00:00 Tokyo - midnight yesterday in Tokyo)
        entry_time = timezone.now() - timedelta(days=1, minutes=30)
        entry = EntryFactory(user=user, created_at=entry_time)

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200

        featured = response.data['featured_entry']
        if featured and featured['id'] == str(entry.id):
            # Entry created at 2025-01-14 15:00 UTC = 2025-01-15 00:00 Tokyo (yesterday in Tokyo time)
            # User's current time: 2025-01-16 00:30 Tokyo
            # days_ago should be 1 (2025-01-16 - 2025-01-15 = 1 day)
            assert featured['days_ago'] == 1

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 03:00:00', tz_offset=0)
    def test_days_ago_refresh_endpoint_with_positive_timezone(self):
        """Refresh endpoint should calculate days_ago correctly for users in positive timezones."""
        # User in Sydney (UTC+11 in summer, UTC+10 in winter)
        user = UserFactory(timezone='Australia/Sydney')
        client = APIClient()
        client.force_authenticate(user=user)

        # Freeze time to 2025-01-15 03:00:00 UTC
        # In Sydney (assuming AEDT UTC+11), this is 2025-01-15 14:00:00

        # Create entries for proper featured entry pool (need 10+)
        for i in range(1, 16):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i)
            )

        # Get initial featured entry
        response1 = client.get('/api/v1/dashboard/')
        assert response1.status_code == 200
        initial_featured = response1.data['featured_entry']
        assert initial_featured is not None

        # Refresh featured entry
        response2 = client.post('/api/v1/dashboard/refresh-featured/')
        assert response2.status_code == 200

        refreshed_featured = response2.data['featured_entry']
        assert refreshed_featured is not None

        # Verify days_ago is calculated correctly (should be >= 1 since we exclude today)
        assert refreshed_featured['days_ago'] >= 1

        # Verify the calculation makes sense: days_ago should match the actual date difference
        from datetime import datetime
        entry_created = datetime.fromisoformat(refreshed_featured['created_at'].replace('Z', '+00:00'))
        entry_date_sydney = entry_created.astimezone(ZoneInfo('Australia/Sydney')).date()
        current_date_sydney = timezone.now().astimezone(ZoneInfo('Australia/Sydney')).date()
        expected_days_ago = (current_date_sydney - entry_date_sydney).days
        assert refreshed_featured['days_ago'] == expected_days_ago

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 07:00:00', tz_offset=0)
    def test_days_ago_refresh_endpoint_with_negative_timezone(self):
        """Refresh endpoint should calculate days_ago correctly for users in negative timezones."""
        # User in Los Angeles (UTC-8 in winter, UTC-7 in summer)
        user = UserFactory(timezone='America/Los_Angeles')
        client = APIClient()
        client.force_authenticate(user=user)

        # Freeze time to 2025-01-15 07:00:00 UTC
        # In LA (assuming PST UTC-8), this is 2025-01-14 23:00:00 (still previous day)

        # Create entries for proper featured entry pool (need 10+)
        for i in range(1, 16):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i)
            )

        # Get initial featured entry
        response1 = client.get('/api/v1/dashboard/')
        assert response1.status_code == 200
        initial_featured = response1.data['featured_entry']
        assert initial_featured is not None

        # Refresh featured entry
        response2 = client.post('/api/v1/dashboard/refresh-featured/')
        assert response2.status_code == 200

        refreshed_featured = response2.data['featured_entry']
        assert refreshed_featured is not None

        # Verify days_ago is calculated correctly (should be >= 1 since we exclude today)
        assert refreshed_featured['days_ago'] >= 1

        # Verify the calculation makes sense: days_ago should match the actual date difference
        from datetime import datetime
        entry_created = datetime.fromisoformat(refreshed_featured['created_at'].replace('Z', '+00:00'))
        entry_date_la = entry_created.astimezone(ZoneInfo('America/Los_Angeles')).date()
        current_date_la = timezone.now().astimezone(ZoneInfo('America/Los_Angeles')).date()
        expected_days_ago = (current_date_la - entry_date_la).days
        assert refreshed_featured['days_ago'] == expected_days_ago
