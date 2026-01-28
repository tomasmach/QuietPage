"""
Tests for real-time streak calculation in DashboardView.

These tests verify that the dashboard shows the correct current streak
even when user hasn't written for multiple days (streak should be 0).
"""
import pytest
from datetime import timedelta
from freezegun import freeze_time
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory


@pytest.mark.integration
@pytest.mark.streak
@pytest.mark.django_db
class TestDashboardStreakRealTime:
    """Tests for real-time streak calculation in dashboard."""

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 12:00:00', tz_offset=0)
    def test_streak_shows_zero_after_gap(self):
        """Streak should be 0 if last entry was 2+ days ago."""
        user = UserFactory(timezone='Europe/Prague')
        client = APIClient()
        client.force_authenticate(user=user)

        # Create entries for 2 consecutive days (3 days ago and 2 days ago)
        # Last entry is from 2025-01-13 (2 days before frozen time)
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=2))
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=3))

        # User model still shows old streak (this simulates the bug)
        user.current_streak = 2
        user.save()

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        
        # Dashboard should show 0 streak (not the cached value from user model)
        assert response.data['stats']['current_streak'] == 0

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 12:00:00', tz_offset=0)
    def test_streak_shows_correct_value_when_written_today(self):
        """Streak should include today when entry exists for today."""
        user = UserFactory(timezone='Europe/Prague')
        client = APIClient()
        client.force_authenticate(user=user)

        # Create entries for 3 consecutive days ending today
        EntryFactory(user=user, created_at=timezone.now())  # Today
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=1))  # Yesterday
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=2))  # 2 days ago

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        assert response.data['stats']['current_streak'] == 3

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 12:00:00', tz_offset=0)
    def test_streak_shows_correct_value_when_written_yesterday(self):
        """Streak should continue if last entry was yesterday (haven't written today yet)."""
        user = UserFactory(timezone='Europe/Prague')
        client = APIClient()
        client.force_authenticate(user=user)

        # Create entries for 3 consecutive days ending yesterday
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=1))  # Yesterday
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=2))  # 2 days ago
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=3))  # 3 days ago

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        # Streak is still 3 because yesterday was written (user can still continue today)
        assert response.data['stats']['current_streak'] == 3

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 12:00:00', tz_offset=0)
    def test_streak_shows_zero_for_no_entries(self):
        """Streak should be 0 when user has no entries."""
        user = UserFactory(timezone='Europe/Prague')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        assert response.data['stats']['current_streak'] == 0

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 12:00:00', tz_offset=0)
    def test_longest_streak_unchanged_from_user_model(self):
        """Longest streak should still come from user model (it's historical)."""
        user = UserFactory(timezone='Europe/Prague', longest_streak=10)
        client = APIClient()
        client.force_authenticate(user=user)

        # No entries, but longest_streak should still be preserved
        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        assert response.data['stats']['longest_streak'] == 10

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 12:00:00', tz_offset=0)
    def test_streak_with_gap_in_past_but_recent_activity(self):
        """Streak should only count consecutive days up to today/yesterday."""
        user = UserFactory(timezone='Europe/Prague')
        client = APIClient()
        client.force_authenticate(user=user)

        # Old streak: 5 days ago to 3 days ago
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=3))
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=4))
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=5))
        
        # Gap on days 2 and 1 ago
        
        # Recent entry: today (new streak)
        EntryFactory(user=user, created_at=timezone.now())

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        # Current streak is just 1 (only today)
        assert response.data['stats']['current_streak'] == 1

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 23:00:00', tz_offset=0)
    def test_streak_respects_user_timezone(self):
        """Streak calculation should respect user's timezone for 'today'."""
        # User in Tokyo (UTC+9) - it's already 2025-01-16 08:00 there
        user = UserFactory(timezone='Asia/Tokyo')
        client = APIClient()
        client.force_authenticate(user=user)

        # Entry at 2025-01-15 15:00 UTC = 2025-01-16 00:00 Tokyo time
        # This counts as "today" for the Tokyo user
        EntryFactory(user=user, created_at=timezone.now() - timedelta(hours=8))

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        # Should be streak of 1 (today in Tokyo timezone)
        assert response.data['stats']['current_streak'] == 1

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 01:00:00', tz_offset=0)
    def test_streak_respects_user_timezone_negative(self):
        """Streak calculation should respect user's timezone for 'yesterday'."""
        # User in Los Angeles (UTC-8) - it's still 2025-01-14 17:00 there
        user = UserFactory(timezone='America/Los_Angeles')
        client = APIClient()
        client.force_authenticate(user=user)

        # Entry from "yesterday" in LA timezone (which is 2 days ago UTC)
        # 2025-01-13 17:00 UTC = 2025-01-14 09:00 LA time (yesterday for LA user)
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=1, hours=8))

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        # Should be streak of 1 (yesterday in LA timezone, user can still write today)
        assert response.data['stats']['current_streak'] == 1

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
    @freeze_time('2025-01-15 12:00:00', tz_offset=0)
    def test_streak_ignores_empty_entries(self):
        """Entries with 0 words should not count toward streak."""
        user = UserFactory(timezone='Europe/Prague')
        client = APIClient()
        client.force_authenticate(user=user)

        # Entry with content (word_count > 0)
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=1), content='some words here')
        # Entry without content (word_count = 0) - created with empty content
        EntryFactory(user=user, created_at=timezone.now() - timedelta(days=2), content='')

        response = client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        # Only yesterday counts (day before was empty)
        assert response.data['stats']['current_streak'] == 1
