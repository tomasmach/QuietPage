"""
Comprehensive pytest tests for statistics API views.

Tests all statistics API endpoints in apps/api/statistics_views.py with 80%+ coverage.
Focuses on mood analytics calculations with timezone awareness and edge cases.
"""

import json
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory

User = get_user_model()


@pytest.mark.statistics
@pytest.mark.unit
class TestStatisticsViewMoodAnalytics:
    """Test StatisticsView with focus on mood analytics calculations."""

    def test_mood_timeline_aggregation(self, client):
        """Mood timeline aggregation returns correct daily averages."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague')).replace(
            hour=12, minute=0, second=0, microsecond=0
        )

        EntryFactory(
            user=user,
            mood_rating=4,
            created_at=base_date
        )
        EntryFactory(
            user=user,
            mood_rating=5,
            created_at=base_date
        )
        EntryFactory(
            user=user,
            mood_rating=2,
            created_at=base_date - timedelta(days=1)
        )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert len(mood_analytics['timeline']) == 2
        assert mood_analytics['total_rated_entries'] == 3

        today_entry = [t for t in mood_analytics['timeline'] if t['date'] == base_date.date().isoformat()][0]
        assert today_entry['average'] == 4.5
        assert today_entry['count'] == 2

        yesterday_entry = [t for t in mood_analytics['timeline'] if t['date'] == (base_date - timedelta(days=1)).date().isoformat()][0]
        assert yesterday_entry['average'] == 2.0
        assert yesterday_entry['count'] == 1

    def test_mood_distribution_calculation(self, client):
        """Distribution calculation correctly counts entries at each mood level."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(user=user, mood_rating=1, created_at=base_date)
        EntryFactory(user=user, mood_rating=1, created_at=base_date)
        EntryFactory(user=user, mood_rating=2, created_at=base_date)
        EntryFactory(user=user, mood_rating=3, created_at=base_date)
        EntryFactory(user=user, mood_rating=4, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert mood_analytics['distribution']['1'] == 2
        assert mood_analytics['distribution']['2'] == 1
        assert mood_analytics['distribution']['3'] == 1
        assert mood_analytics['distribution']['4'] == 1
        assert mood_analytics['distribution']['5'] == 3

    def test_mood_average_excludes_null_ratings(self, client):
        """Average calculation handles null mood ratings (excluded from average)."""
        from apps.journal.tests.factories import EntryWithoutMoodFactory

        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(user=user, mood_rating=4, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)
        EntryWithoutMoodFactory(user=user, created_at=base_date)
        EntryWithoutMoodFactory(user=user, created_at=base_date)

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert mood_analytics['average'] == 4.5
        assert mood_analytics['total_rated_entries'] == 2

    def test_trend_detection_improving(self, client):
        """Trend detection correctly identifies improving pattern."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        for i in range(5):
            rating = 1 + i
            EntryFactory(
                user=user,
                mood_rating=rating,
                created_at=base_date - timedelta(days=4-i)
            )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert mood_analytics['trend'] == 'improving'

    def test_trend_detection_declining(self, client):
        """Trend detection correctly identifies declining pattern."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        for i in range(5):
            rating = 5 - i
            EntryFactory(
                user=user,
                mood_rating=rating,
                created_at=base_date - timedelta(days=4-i)
            )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert mood_analytics['trend'] == 'declining'

    def test_trend_detection_stable(self, client):
        """Trend detection correctly identifies stable pattern."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        for i in range(5):
            EntryFactory(
                user=user,
                mood_rating=3,
                created_at=base_date - timedelta(days=i)
            )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert mood_analytics['trend'] == 'stable'

    def test_trend_detection_threshold(self, client):
        """Trend detection uses correct threshold (0.3) for significance."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        entries = []
        for i in range(4):
            entries.append(EntryFactory(
                user=user,
                mood_rating=3,
                created_at=base_date - timedelta(days=3 - i)
            ))

        for i in range(4):
            entries.append(EntryFactory(
                user=user,
                mood_rating=3.2,
                created_at=base_date - timedelta(days=7 - i)
            ))

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert mood_analytics['trend'] == 'stable'

    def test_timezone_awareness_midnight_grouping(self, client):
        """Entries respect user's timezone when grouping by date."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        user_tz = ZoneInfo(str(user.timezone))
        today = timezone.now().astimezone(user_tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        EntryFactory(
            user=user,
            mood_rating=4,
            created_at=today + timedelta(hours=12)
        )

        EntryFactory(
            user=user,
            mood_rating=5,
            created_at=today - timedelta(days=1) + timedelta(hours=12)
        )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert len(mood_analytics['timeline']) == 2
        assert all('average' in day for day in mood_analytics['timeline'])

    def test_timezone_awareness_day_boundary(self, client):
        """Entries near day boundary respect user's local timezone."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        user_tz = ZoneInfo('Europe/Prague')
        today_midnight = timezone.now().astimezone(user_tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        entry_before = EntryFactory(
            user=user,
            mood_rating=3,
            created_at=today_midnight - timedelta(seconds=1)
        )

        entry_after = EntryFactory(
            user=user,
            mood_rating=4,
            created_at=today_midnight + timedelta(seconds=1)
        )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert len(mood_analytics['timeline']) == 2

        today_date = today_midnight.date().isoformat()
        yesterday_date = (today_midnight - timedelta(days=1)).date().isoformat()

        today_entry = [t for t in mood_analytics['timeline'] if t['date'] == today_date][0]
        yesterday_entry = [t for t in mood_analytics['timeline'] if t['date'] == yesterday_date][0]

        assert today_entry['average'] == 4.0
        assert yesterday_entry['average'] == 3.0

    def test_no_mood_ratings_returns_empty_analytics(self, client):
        """User with no mood ratings returns empty analytics."""
        from apps.journal.tests.factories import EntryWithoutMoodFactory

        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        EntryWithoutMoodFactory.create_batch(5, user=user)

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert mood_analytics['average'] is None
        assert mood_analytics['total_rated_entries'] == 0
        assert mood_analytics['distribution'] == {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        assert mood_analytics['timeline'] == []
        assert mood_analytics['trend'] == 'stable'

    def test_single_day_mood_analytics(self, client):
        """Single day with multiple entries calculates correct average."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(user=user, mood_rating=2, created_at=base_date)
        EntryFactory(user=user, mood_rating=4, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert len(mood_analytics['timeline']) == 1
        assert mood_analytics['timeline'][0]['average'] == 3.67
        assert mood_analytics['timeline'][0]['count'] == 3
        assert mood_analytics['average'] == 3.67
        assert mood_analytics['total_rated_entries'] == 3
        assert mood_analytics['trend'] == 'stable'

    def test_period_filtering_respects_date_range(self, client):
        """Period parameter correctly filters entries by date range."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        old_entry = EntryFactory(
            user=user,
            mood_rating=5,
            created_at=base_date - timedelta(days=20)
        )

        recent_entries = EntryFactory.create_batch(
            5,
            user=user,
            mood_rating=3,
            created_at=base_date - timedelta(days=1)
        )

        response_7d = client.get(reverse('api:statistics'), {'period': '7d'})
        response_30d = client.get(reverse('api:statistics'), {'period': '30d'})

        assert response_7d.status_code == 200
        assert response_30d.status_code == 200

        data_7d = response_7d.json()
        data_30d = response_30d.json()

        assert data_7d['mood_analytics']['total_rated_entries'] == 5
        assert data_30d['mood_analytics']['total_rated_entries'] == 6

    def test_invalid_period_returns_error(self, client):
        """Invalid period parameter returns 400 error."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': 'invalid'})

        assert response.status_code == 400
        data = response.json()
        assert 'error' in data

    def test_all_period_includes_all_entries(self, client):
        """'all' period includes all user entries regardless of date."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(
            user=user,
            mood_rating=1,
            created_at=base_date - timedelta(days=400)
        )
        EntryFactory(
            user=user,
            mood_rating=5,
            created_at=base_date
        )

        response = client.get(reverse('api:statistics'), {'period': 'all'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert mood_analytics['total_rated_entries'] == 2
        assert mood_analytics['average'] == 3.0

    def test_requires_authentication(self, client):
        """Unauthenticated users cannot access statistics."""
        response = client.get(reverse('api:statistics'))

        assert response.status_code == 403

    def test_user_isolation(self, client):
        """Statistics only include current user's entries."""
        user1 = UserFactory(timezone='Europe/Prague')
        user2 = UserFactory(timezone='Europe/Prague')
        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(user=user1, mood_rating=5, created_at=base_date)
        EntryFactory(user=user1, mood_rating=5, created_at=base_date)
        EntryFactory(user=user2, mood_rating=1, created_at=base_date)

        client.force_login(user1)
        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data['mood_analytics']

        assert mood_analytics['total_rated_entries'] == 2
        assert mood_analytics['average'] == 5.0

    def test_word_count_analytics_calculations(self, client):
        """Word count analytics calculate correctly."""
        user = UserFactory(timezone='Europe/Prague', daily_word_goal=100)
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        entry1 = EntryFactory(
            user=user,
            content='This is a test entry with ten words.',
            created_at=base_date - timedelta(days=1)
        )
        entry1.refresh_from_db()

        entry2 = EntryFactory(
            user=user,
            content='Another entry with fifteen words in total here.',
            created_at=base_date
        )
        entry2.refresh_from_db()

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        assert word_analytics['total'] == entry1.word_count + entry2.word_count
        assert word_analytics['total_entries'] == 2
        assert word_analytics['average_per_entry'] == (entry1.word_count + entry2.word_count) / 2
        assert len(word_analytics['timeline']) == 2

    def test_caching_headers(self, client):
        """Response includes correct caching headers."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        assert 'Cache-Control' in response
        assert 'max-age=1800' in response['Cache-Control']
        assert 'Vary' in response
        assert 'Authorization' in response['Vary']
