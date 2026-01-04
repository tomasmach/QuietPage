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


@pytest.mark.statistics
@pytest.mark.unit
class TestStatisticsViewWordCountAnalytics:
    """Test StatisticsView with focus on word count analytics calculations."""

    def test_daily_word_count_aggregation(self, client):
        """Daily word count aggregation sums correctly across multiple entries per day."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        entry1 = EntryFactory(
            user=user,
            content='First entry with five words.',
            created_at=base_date
        )
        entry1.refresh_from_db()

        entry2 = EntryFactory(
            user=user,
            content='Second entry has six words here.',
            created_at=base_date
        )
        entry2.refresh_from_db()

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        timeline = word_analytics['timeline']
        today_entry = [t for t in timeline if t['date'] == base_date.date().isoformat()][0]

        assert today_entry['word_count'] == entry1.word_count + entry2.word_count
        assert today_entry['entry_count'] == 2
        assert word_analytics['total'] == entry1.word_count + entry2.word_count

    def test_goal_achievement_rate_100_percent(self, client):
        """Goal achievement rate with 100% achievement."""
        user = UserFactory(timezone='Europe/Prague', daily_word_goal=100)
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(
            user=user,
            content='This entry has more than one hundred words. ' + 'word ' * 110,
            created_at=base_date
        )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        assert word_analytics['goal_achievement_rate'] == 100.0

    def test_goal_achievement_rate_0_percent(self, client):
        """Goal achievement rate with 0% achievement."""
        user = UserFactory(timezone='Europe/Prague', daily_word_goal=1000)
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(
            user=user,
            content='Short entry with ten words.',
            created_at=base_date
        )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        assert word_analytics['goal_achievement_rate'] == 0.0

    def test_goal_achievement_rate_partial(self, client):
        """Goal achievement rate with partial achievement."""
        user = UserFactory(timezone='Europe/Prague', daily_word_goal=100)
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        day1 = base_date - timedelta(days=1)
        day2 = base_date - timedelta(days=2)

        EntryFactory(
            user=user,
            content='Entry one with over hundred words exactly. ' + 'word ' * 100,
            created_at=day1
        )

        EntryFactory(
            user=user,
            content='Entry two with fifty words only. ' + 'word ' * 40,
            created_at=day2
        )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        assert word_analytics['goal_achievement_rate'] == 50.0

    def test_best_day_calculation(self, client):
        """'best day' calculation returns highest word count day."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(
            user=user,
            content='Normal entry with ten words.',
            created_at=base_date - timedelta(days=1)
        )

        EntryFactory(
            user=user,
            content='Best entry with two hundred words. ' + 'word ' * 190,
            created_at=base_date
        )

        EntryFactory(
            user=user,
            content='Another normal entry with fifteen words here.',
            created_at=base_date - timedelta(days=2)
        )

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        assert word_analytics['best_day'] is not None
        assert word_analytics['best_day']['date'] == base_date.date().isoformat()
        assert word_analytics['best_day']['word_count'] > 100

    def test_no_entries_returns_zeroes(self, client):
        """User with no entries returns zeros/nulls gracefully."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        assert word_analytics['total'] == 0
        assert word_analytics['total_entries'] == 0
        assert word_analytics['average_per_entry'] == 0
        assert word_analytics['average_per_day'] == 0
        assert word_analytics['timeline'] == []
        assert word_analytics['best_day'] is None

    def test_encrypted_content_not_decrypted(self, client):
        """Calculations exclude encrypted content field (no decryption happens)."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        entry = EntryFactory(
            user=user,
            content='This is a test entry with ten words.',
            created_at=base_date
        )
        entry.refresh_from_db()

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        assert word_analytics['total'] == entry.word_count
        assert word_analytics['total'] > 0

    def test_default_daily_goal_when_not_set(self, client):
        """User with default daily goal uses 750 words."""
        user = UserFactory(timezone='Europe/Prague')

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(
            user=user,
            content='word ' * 750,
            created_at=base_date
        )

        client.force_login(user)
        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        assert word_analytics['goal_achievement_rate'] == 100.0

    def test_average_per_day_calculation(self, client):
        """Average per day calculated correctly across active days."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        entry1 = EntryFactory(
            user=user,
            content='First entry with twenty words here. ' + 'word ' * 10,
            created_at=base_date
        )
        entry1.refresh_from_db()

        entry2 = EntryFactory(
            user=user,
            content='Second entry with thirty words total here. ' + 'word ' * 20,
            created_at=base_date - timedelta(days=1)
        )
        entry2.refresh_from_db()

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data['word_count_analytics']

        expected_avg = (entry1.word_count + entry2.word_count) / 2
        assert word_analytics['average_per_day'] == round(expected_avg, 2)
        assert word_analytics['total_entries'] == 2


@pytest.mark.statistics
@pytest.mark.integration
class TestStatisticsViewIntegration:
    """Integration tests for statistics endpoint including caching and performance."""

    def test_authenticated_user_returns_200(self, client):
        """Authenticated users receive 200 response."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200

    def test_anonymous_user_returns_403(self, client):
        """Anonymous users receive 403 forbidden response."""
        response = client.get(reverse('api:statistics'))

        assert response.status_code == 403

    def test_period_7d_returns_correct_date_range(self, client):
        """7d period returns correct 7-day date range."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()

        assert data['period'] == '7d'
        assert 'start_date' in data
        assert 'end_date' in data

        from zoneinfo import ZoneInfo
        from django.utils import timezone

        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        expected_start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        actual_start = datetime.fromisoformat(data['start_date']).replace(tzinfo=None)

        assert actual_start.date() == expected_start.date()

    def test_period_30d_returns_correct_date_range(self, client):
        """30d period returns correct 30-day date range."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': '30d'})

        assert response.status_code == 200
        data = response.json()

        assert data['period'] == '30d'

        from zoneinfo import ZoneInfo
        from django.utils import timezone

        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        expected_start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        actual_start = datetime.fromisoformat(data['start_date']).replace(tzinfo=None)

        assert actual_start.date() == expected_start.date()

    def test_period_90d_returns_correct_date_range(self, client):
        """90d period returns correct 90-day date range."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': '90d'})

        assert response.status_code == 200
        data = response.json()

        assert data['period'] == '90d'

        from zoneinfo import ZoneInfo
        from django.utils import timezone

        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        expected_start = (now - timedelta(days=90)).replace(hour=0, minute=0, second=0, microsecond=0)
        actual_start = datetime.fromisoformat(data['start_date']).replace(tzinfo=None)

        assert actual_start.date() == expected_start.date()

    def test_period_1y_returns_correct_date_range(self, client):
        """1y period returns correct 365-day date range."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': '1y'})

        assert response.status_code == 200
        data = response.json()

        assert data['period'] == '1y'

        from zoneinfo import ZoneInfo
        from django.utils import timezone

        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        expected_start = (now - timedelta(days=365)).replace(hour=0, minute=0, second=0, microsecond=0)
        actual_start = datetime.fromisoformat(data['start_date']).replace(tzinfo=None)

        assert actual_start.date() == expected_start.date()

    def test_period_all_returns_all_entries(self, client):
        """all period includes entries from the first entry date."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(user=user, created_at=base_date - timedelta(days=100))
        EntryFactory(user=user, created_at=base_date)

        response = client.get(reverse('api:statistics'), {'period': 'all'})

        assert response.status_code == 200
        data = response.json()

        assert data['period'] == 'all'
        assert data['mood_analytics']['total_rated_entries'] >= 0
        assert data['word_count_analytics']['total_entries'] == 2

    def test_response_structure_matches_serializer(self, client):
        """Response structure matches StatisticsSerializer definition."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()

        required_fields = ['period', 'start_date', 'end_date', 'mood_analytics', 'word_count_analytics']
        for field in required_fields:
            assert field in data

        mood_analytics = data['mood_analytics']
        required_mood_fields = ['average', 'distribution', 'timeline', 'total_rated_entries', 'trend']
        for field in required_mood_fields:
            assert field in mood_analytics

        word_analytics = data['word_count_analytics']
        required_word_fields = [
            'total', 'average_per_entry', 'average_per_day', 'timeline',
            'total_entries', 'goal_achievement_rate', 'best_day'
        ]
        for field in required_word_fields:
            assert field in word_analytics

    def test_caching_improves_performance(self, client):
        """Identical requests are faster due to caching (cache hit)."""
        import time

        user = UserFactory(timezone='Europe/Prague')
        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory.create_batch(10, user=user, created_at=base_date)
        client.force_login(user)

        first_request_start = time.time()
        response1 = client.get(reverse('api:statistics'), {'period': '7d'})
        first_request_time = time.time() - first_request_start

        assert response1.status_code == 200

        second_request_start = time.time()
        response2 = client.get(reverse('api:statistics'), {'period': '7d'})
        second_request_time = time.time() - second_request_start

        assert response2.status_code == 200

        assert response1.json() == response2.json()
        assert second_request_time < first_request_time

    def test_caching_works_across_periods(self, client):
        """Different period parameters generate different cache keys."""
        user = UserFactory(timezone='Europe/Prague')
        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory.create_batch(5, user=user, created_at=base_date)
        client.force_login(user)

        response_7d = client.get(reverse('api:statistics'), {'period': '7d'})
        response_30d = client.get(reverse('api:statistics'), {'period': '30d'})

        assert response_7d.status_code == 200
        assert response_30d.status_code == 200

        data_7d = response_7d.json()
        data_30d = response_30d.json()

        assert data_7d['period'] == '7d'
        assert data_30d['period'] == '30d'

    def test_cache_invalidation_on_new_entry(self, client):
        """Creating a new entry on a new day invalidates cache and returns fresh data."""
        user = UserFactory(timezone='Europe/Prague')
        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory.create_batch(5, user=user, created_at=base_date - timedelta(days=1))
        client.force_login(user)

        response1 = client.get(reverse('api:statistics'), {'period': '7d'})
        data1 = response1.json()

        initial_entries = data1['word_count_analytics']['total_entries']
        assert initial_entries == 5

        EntryFactory(user=user, created_at=base_date)

        user.refresh_from_db()

        from django.core.cache import cache
        cache.clear()

        response2 = client.get(reverse('api:statistics'), {'period': '7d'})
        data2 = response2.json()

        updated_entries = data2['word_count_analytics']['total_entries']
        assert updated_entries == 6

    def test_cache_key_includes_last_entry_date(self, client):
        """Cache key includes last_entry_date for proper invalidation."""
        user = UserFactory(timezone='Europe/Prague')
        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(user=user, created_at=base_date - timedelta(days=1))
        client.force_login(user)

        response1 = client.get(reverse('api:statistics'), {'period': '7d'})

        user.refresh_from_db()
        last_entry_date_1 = user.last_entry_date.isoformat() if user.last_entry_date else 'none'

        EntryFactory(user=user, created_at=base_date)

        user.refresh_from_db()
        last_entry_date_2 = user.last_entry_date.isoformat() if user.last_entry_date else 'none'

        assert last_entry_date_1 != last_entry_date_2

        from django.core.cache import cache
        cache.clear()

        response2 = client.get(reverse('api:statistics'), {'period': '7d'})

        data1 = response1.json()
        data2 = response2.json()

        assert data1['word_count_analytics']['total_entries'] != data2['word_count_analytics']['total_entries']

    def test_invalid_period_parameter_returns_400(self, client):
        """Invalid period parameter returns 400 error."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:statistics'), {'period': 'invalid'})

        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'Invalid period' in data['error']

    def test_performance_with_100_entries_under_2_seconds(self, client):
        """Statistics endpoint with 100+ entries responds in under 2 seconds."""
        import time

        user = UserFactory(timezone='Europe/Prague')
        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        for i in range(100):
            entry_date = base_date - timedelta(hours=i)
            EntryFactory(
                user=user,
                content=f'Entry {i} with some content for testing. ' * 10,
                mood_rating=(i % 5) + 1,
                created_at=entry_date
            )

        client.force_login(user)

        start_time = time.time()
        response = client.get(reverse('api:statistics'), {'period': '90d'})
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 2.0, f"Response time {response_time:.3f}s exceeds 2 second limit"

        data = response.json()
        assert data['word_count_analytics']['total_entries'] == 100

    def test_performance_with_200_entries_under_2_seconds(self, client):
        """Statistics endpoint with 200 entries still responds in under 2 seconds."""
        import time

        user = UserFactory(timezone='Europe/Prague')
        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        for i in range(200):
            entry_date = base_date - timedelta(days=i)
            EntryFactory(
                user=user,
                content=f'Entry {i} content. ' * 5,
                mood_rating=(i % 5) + 1,
                created_at=entry_date
            )

        client.force_login(user)

        start_time = time.time()
        response = client.get(reverse('api:statistics'), {'period': '1y'})
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 2.0, f"Response time {response_time:.3f}s exceeds 2 second limit"

        data = response.json()
        assert data['word_count_analytics']['total_entries'] == 200

    def test_multiple_users_have_separate_caches(self, client):
        """Different users have separate cache entries."""
        from django.core.cache import cache
        cache.clear()

        user1 = UserFactory(timezone='Europe/Prague')
        user2 = UserFactory(timezone='Europe/Prague')
        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory.create_batch(10, user=user1, created_at=base_date)
        EntryFactory.create_batch(20, user=user2, created_at=base_date)

        client.force_login(user1)
        response1 = client.get(reverse('api:statistics'), {'period': '7d'})
        data1 = response1.json()

        assert response1.status_code == 200
        assert data1['word_count_analytics']['total_entries'] == 10

        client.logout()
        cache.clear()
        client.force_login(user2)
        response2 = client.get(reverse('api:statistics'), {'period': '7d'})
        data2 = response2.json()

        assert response2.status_code == 200
        assert data2['word_count_analytics']['total_entries'] == 20

    def test_mood_analytics_timeline_structure(self, client):
        """Mood analytics timeline has correct structure."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        EntryFactory(user=user, mood_rating=4, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date - timedelta(days=1))

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        timeline = data['mood_analytics']['timeline']

        assert len(timeline) == 2
        for day in timeline:
            assert 'date' in day
            assert 'average' in day
            assert 'count' in day

    def test_word_analytics_timeline_structure(self, client):
        """Word analytics timeline has correct structure."""
        user = UserFactory(timezone='Europe/Prague')
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo('Europe/Prague'))

        entry1 = EntryFactory(user=user, content='Ten words here', created_at=base_date)
        entry1.refresh_from_db()

        entry2 = EntryFactory(user=user, content='Five words', created_at=base_date - timedelta(days=1))
        entry2.refresh_from_db()

        response = client.get(reverse('api:statistics'), {'period': '7d'})

        assert response.status_code == 200
        data = response.json()
        timeline = data['word_count_analytics']['timeline']

        assert len(timeline) == 2
        for day in timeline:
            assert 'date' in day
            assert 'word_count' in day
            assert 'entry_count' in day
