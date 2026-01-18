"""
Tests for FeaturedEntry selection and refresh logic in DashboardView.
"""
import pytest
from datetime import timedelta
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
