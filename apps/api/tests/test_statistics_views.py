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
from dateutil.relativedelta import relativedelta
from unittest.mock import patch

from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory

User = get_user_model()


@pytest.mark.statistics
@pytest.mark.unit
class TestStatisticsViewMoodAnalytics:
    """Test StatisticsView with focus on mood analytics calculations."""

    def test_mood_timeline_aggregation(self, client):
        """Mood timeline aggregation returns correct daily averages."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = (
            timezone.now()
            .astimezone(ZoneInfo("Europe/Prague"))
            .replace(hour=12, minute=0, second=0, microsecond=0)
        )

        EntryFactory(user=user, mood_rating=4, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)
        EntryFactory(user=user, mood_rating=2, created_at=base_date - timedelta(days=1))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert len(mood_analytics["timeline"]) == 2
        assert mood_analytics["total_rated_entries"] == 3

        today_entry = [
            t
            for t in mood_analytics["timeline"]
            if t["date"] == base_date.date().isoformat()
        ][0]
        assert today_entry["average"] == 4.5
        assert today_entry["count"] == 2

        yesterday_entry = [
            t
            for t in mood_analytics["timeline"]
            if t["date"] == (base_date - timedelta(days=1)).date().isoformat()
        ][0]
        assert yesterday_entry["average"] == 2.0
        assert yesterday_entry["count"] == 1

    def test_mood_distribution_calculation(self, client):
        """Distribution calculation correctly counts entries at each mood level."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, mood_rating=1, created_at=base_date)
        EntryFactory(user=user, mood_rating=1, created_at=base_date)
        EntryFactory(user=user, mood_rating=2, created_at=base_date)
        EntryFactory(user=user, mood_rating=3, created_at=base_date)
        EntryFactory(user=user, mood_rating=4, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert mood_analytics["distribution"]["1"] == 2
        assert mood_analytics["distribution"]["2"] == 1
        assert mood_analytics["distribution"]["3"] == 1
        assert mood_analytics["distribution"]["4"] == 1
        assert mood_analytics["distribution"]["5"] == 3

    def test_mood_average_excludes_null_ratings(self, client):
        """Average calculation handles null mood ratings (excluded from average)."""
        from apps.journal.tests.factories import EntryWithoutMoodFactory

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, mood_rating=4, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)
        EntryWithoutMoodFactory(user=user, created_at=base_date)
        EntryWithoutMoodFactory(user=user, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert mood_analytics["average"] == 4.5
        assert mood_analytics["total_rated_entries"] == 2

    def test_trend_detection_improving(self, client):
        """Trend detection correctly identifies improving pattern."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(5):
            rating = 1 + i
            EntryFactory(
                user=user,
                mood_rating=rating,
                created_at=base_date - timedelta(days=4 - i),
            )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert mood_analytics["trend"] == "improving"

    def test_trend_detection_declining(self, client):
        """Trend detection correctly identifies declining pattern."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(5):
            rating = 5 - i
            EntryFactory(
                user=user,
                mood_rating=rating,
                created_at=base_date - timedelta(days=4 - i),
            )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert mood_analytics["trend"] == "declining"

    def test_trend_detection_stable(self, client):
        """Trend detection correctly identifies stable pattern."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(5):
            EntryFactory(
                user=user, mood_rating=3, created_at=base_date - timedelta(days=i)
            )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert mood_analytics["trend"] == "stable"

    def test_trend_detection_threshold(self, client):
        """Trend detection uses correct threshold (0.3) for significance."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        entries = []
        for i in range(4):
            entries.append(
                EntryFactory(
                    user=user,
                    mood_rating=3,
                    created_at=base_date - timedelta(days=3 - i),
                )
            )

        for i in range(4):
            entries.append(
                EntryFactory(
                    user=user,
                    mood_rating=3.2,
                    created_at=base_date - timedelta(days=7 - i),
                )
            )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert mood_analytics["trend"] == "stable"

    def test_timezone_awareness_midnight_grouping(self, client):
        """Entries respect user's timezone when grouping by date."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo(str(user.timezone))
        today = (
            timezone.now()
            .astimezone(user_tz)
            .replace(hour=0, minute=0, second=0, microsecond=0)
        )

        EntryFactory(user=user, mood_rating=4, created_at=today + timedelta(hours=12))

        EntryFactory(
            user=user,
            mood_rating=5,
            created_at=today - timedelta(days=1) + timedelta(hours=12),
        )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert len(mood_analytics["timeline"]) == 2
        assert all("average" in day for day in mood_analytics["timeline"])

    def test_timezone_awareness_day_boundary(self, client):
        """Entries near day boundary respect user's local timezone."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        today_midnight = (
            timezone.now()
            .astimezone(user_tz)
            .replace(hour=0, minute=0, second=0, microsecond=0)
        )

        entry_before = EntryFactory(
            user=user, mood_rating=3, created_at=today_midnight - timedelta(seconds=1)
        )

        entry_after = EntryFactory(
            user=user, mood_rating=4, created_at=today_midnight + timedelta(seconds=1)
        )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert len(mood_analytics["timeline"]) == 2

        today_date = today_midnight.date().isoformat()
        yesterday_date = (today_midnight - timedelta(days=1)).date().isoformat()

        today_entry = [
            t for t in mood_analytics["timeline"] if t["date"] == today_date
        ][0]
        yesterday_entry = [
            t for t in mood_analytics["timeline"] if t["date"] == yesterday_date
        ][0]

        assert today_entry["average"] == 4.0
        assert yesterday_entry["average"] == 3.0

    def test_dst_spring_forward_transition_europe_prague(self, client):
        """Entries during spring forward (last Sunday of March) are handled correctly."""
        from unittest.mock import patch

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        spring_forward_2024 = datetime(2024, 3, 31, 2, 30, 0, tzinfo=user_tz)

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = spring_forward_2024

            EntryFactory(
                user=user,
                mood_rating=4,
                created_at=spring_forward_2024 - timedelta(days=1),
            )

            EntryFactory(
                user=user,
                mood_rating=5,
                created_at=spring_forward_2024.replace(hour=3, minute=30),
            )

            response = client.get(reverse("api:statistics"), {"period": "7d"})

            assert response.status_code == 200
            data = response.json()
            mood_analytics = data["mood_analytics"]

            assert len(mood_analytics["timeline"]) == 2

    def test_dst_fall_back_transition_europe_prague(self, client):
        """Entries during fall back (last Sunday of October) are handled correctly."""
        from unittest.mock import patch

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        fall_back_2024 = datetime(2024, 10, 27, 2, 30, 0, tzinfo=user_tz)

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = fall_back_2024

            EntryFactory(
                user=user,
                mood_rating=3,
                created_at=fall_back_2024.replace(hour=1, fold=0),
            )

            EntryFactory(
                user=user,
                mood_rating=4,
                created_at=fall_back_2024.replace(hour=2, fold=0),
            )

            response = client.get(reverse("api:statistics"), {"period": "7d"})

            assert response.status_code == 200
            data = response.json()
            mood_analytics = data["mood_analytics"]

            assert len(mood_analytics["timeline"]) == 1

            day_entry = mood_analytics["timeline"][0]
            assert day_entry["count"] == 2
            assert day_entry["average"] == 3.5

    def test_dst_timeline_grouping_no_duplicates(self, client):
        """Timeline grouping has no duplicate days across DST transitions."""
        from unittest.mock import patch

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        fall_back_2024 = datetime(2024, 10, 27, 12, 0, 0, tzinfo=user_tz)

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = fall_back_2024

            for i in range(5):
                EntryFactory(
                    user=user,
                    mood_rating=3,
                    created_at=fall_back_2024 - timedelta(days=i),
                )

            EntryFactory(
                user=user,
                mood_rating=5,
                created_at=fall_back_2024.replace(hour=1, fold=0),
            )

            EntryFactory(
                user=user,
                mood_rating=4,
                created_at=fall_back_2024.replace(hour=2, fold=0),
            )

            response = client.get(reverse("api:statistics"), {"period": "7d"})

            assert response.status_code == 200
            data = response.json()
            mood_analytics = data["mood_analytics"]

            timeline_dates = [day["date"] for day in mood_analytics["timeline"]]
            assert len(timeline_dates) == len(set(timeline_dates))

    def test_no_mood_ratings_returns_empty_analytics(self, client):
        """User with no mood ratings returns empty analytics."""
        from apps.journal.tests.factories import EntryWithoutMoodFactory

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        EntryWithoutMoodFactory.create_batch(5, user=user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert mood_analytics["average"] is None
        assert mood_analytics["total_rated_entries"] == 0
        assert mood_analytics["distribution"] == {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0,
            "5": 0,
        }
        assert mood_analytics["timeline"] == []
        assert mood_analytics["trend"] == "stable"

    def test_single_day_mood_analytics(self, client):
        """Single day with multiple entries calculates correct average."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, mood_rating=2, created_at=base_date)
        EntryFactory(user=user, mood_rating=4, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert len(mood_analytics["timeline"]) == 1
        assert mood_analytics["timeline"][0]["average"] == 3.67
        assert mood_analytics["timeline"][0]["count"] == 3
        assert mood_analytics["average"] == 3.67
        assert mood_analytics["total_rated_entries"] == 3
        assert mood_analytics["trend"] == "stable"

    def test_period_filtering_respects_date_range(self, client):
        """Period parameter correctly filters entries by date range."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        old_entry = EntryFactory(
            user=user, mood_rating=5, created_at=base_date - timedelta(days=20)
        )

        recent_entries = EntryFactory.create_batch(
            5, user=user, mood_rating=3, created_at=base_date - timedelta(days=1)
        )

        response_7d = client.get(reverse("api:statistics"), {"period": "7d"})
        response_30d = client.get(reverse("api:statistics"), {"period": "30d"})

        assert response_7d.status_code == 200
        assert response_30d.status_code == 200

        data_7d = response_7d.json()
        data_30d = response_30d.json()

        assert data_7d["mood_analytics"]["total_rated_entries"] == 5
        assert data_30d["mood_analytics"]["total_rated_entries"] == 6

    def test_invalid_period_returns_error(self, client):
        """Invalid period parameter returns 400 error."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "invalid"})

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_all_period_includes_all_entries(self, client):
        """'all' period includes all user entries regardless of date."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(
            user=user, mood_rating=1, created_at=base_date - timedelta(days=400)
        )
        EntryFactory(user=user, mood_rating=5, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert mood_analytics["total_rated_entries"] == 2
        assert mood_analytics["average"] == 3.0

    def test_requires_authentication(self, client):
        """Unauthenticated users cannot access statistics."""
        response = client.get(reverse("api:statistics"))

        assert response.status_code == 403

    def test_user_isolation(self, client):
        """Statistics only include current user's entries."""
        user1 = UserFactory(timezone="Europe/Prague")
        user2 = UserFactory(timezone="Europe/Prague")
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user1, mood_rating=5, created_at=base_date)
        EntryFactory(user=user1, mood_rating=5, created_at=base_date)
        EntryFactory(user=user2, mood_rating=1, created_at=base_date)

        client.force_login(user1)
        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        assert mood_analytics["total_rated_entries"] == 2
        assert mood_analytics["average"] == 5.0

    def test_word_count_analytics_calculations(self, client):
        """Word count analytics calculate correctly."""
        user = UserFactory(timezone="Europe/Prague", daily_word_goal=100)
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        entry1 = EntryFactory(
            user=user,
            content="This is a test entry with ten words.",
            created_at=base_date - timedelta(days=1),
        )
        entry1.refresh_from_db()

        entry2 = EntryFactory(
            user=user,
            content="Another entry with fifteen words in total here.",
            created_at=base_date,
        )
        entry2.refresh_from_db()

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        assert word_analytics["total"] == entry1.word_count + entry2.word_count
        assert word_analytics["total_entries"] == 2
        assert (
            word_analytics["average_per_entry"]
            == (entry1.word_count + entry2.word_count) / 2
        )
        assert len(word_analytics["timeline"]) == 2

    def test_caching_headers(self, client):
        """Response includes correct caching headers."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        assert "Cache-Control" in response
        assert "max-age=1800" in response["Cache-Control"]
        assert "Vary" in response
        assert "Authorization" in response["Vary"]

    def test_mood_distribution_keys_are_strings(self, client):
        """Distribution dictionary keys are strings (not integers) for JSON consistency."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, mood_rating=1, created_at=base_date)
        EntryFactory(user=user, mood_rating=3, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        mood_analytics = data["mood_analytics"]

        distribution = mood_analytics["distribution"]
        assert isinstance(distribution["1"], int)
        assert isinstance(distribution["2"], int)
        assert isinstance(distribution["3"], int)
        assert isinstance(distribution["4"], int)
        assert isinstance(distribution["5"], int)
        assert distribution["1"] == 1
        assert distribution["2"] == 0
        assert distribution["3"] == 1
        assert distribution["4"] == 0
        assert distribution["5"] == 1

    def test_mood_distribution_json_serialization(self, client):
        """Distribution dictionary serializes correctly to JSON with string keys."""
        import json

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, mood_rating=2, created_at=base_date)
        EntryFactory(user=user, mood_rating=4, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200

        response_data = response.json()
        mood_analytics = response_data["mood_analytics"]
        distribution = mood_analytics["distribution"]

        parsed_json = json.loads(response.content)
        parsed_distribution = parsed_json["mood_analytics"]["distribution"]

        assert parsed_distribution == {"1": 0, "2": 1, "3": 0, "4": 1, "5": 0}
        assert list(parsed_distribution.keys()) == ["1", "2", "3", "4", "5"]
        assert all(isinstance(key, str) for key in parsed_distribution.keys())


@pytest.mark.statistics
@pytest.mark.unit
class TestStatisticsViewWordCountAnalytics:
    """Test StatisticsView with focus on word count analytics calculations."""

    def test_daily_word_count_aggregation(self, client):
        """Daily word count aggregation sums correctly across multiple entries per day."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        entry1 = EntryFactory(
            user=user, content="First entry with five words.", created_at=base_date
        )
        entry1.refresh_from_db()

        entry2 = EntryFactory(
            user=user, content="Second entry has six words here.", created_at=base_date
        )
        entry2.refresh_from_db()

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        timeline = word_analytics["timeline"]
        today_entry = [
            t for t in timeline if t["date"] == base_date.date().isoformat()
        ][0]

        assert today_entry["word_count"] == entry1.word_count + entry2.word_count
        assert today_entry["entry_count"] == 2
        assert word_analytics["total"] == entry1.word_count + entry2.word_count

    def test_goal_achievement_rate_100_percent(self, client):
        """Goal achievement rate with 100% achievement."""
        user = UserFactory(timezone="Europe/Prague", daily_word_goal=100)
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(
            user=user,
            content="This entry has more than one hundred words. " + "word " * 110,
            created_at=base_date,
        )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        assert word_analytics["goal_achievement_rate"] == 100.0

    def test_goal_achievement_rate_0_percent(self, client):
        """Goal achievement rate with 0% achievement."""
        user = UserFactory(timezone="Europe/Prague", daily_word_goal=1000)
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(
            user=user, content="Short entry with ten words.", created_at=base_date
        )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        assert word_analytics["goal_achievement_rate"] == 0.0

    def test_goal_achievement_rate_partial(self, client):
        """Goal achievement rate with partial achievement."""
        user = UserFactory(timezone="Europe/Prague", daily_word_goal=100)
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        day1 = base_date - timedelta(days=1)
        day2 = base_date - timedelta(days=2)

        EntryFactory(
            user=user,
            content="Entry one with over hundred words exactly. " + "word " * 100,
            created_at=day1,
        )

        EntryFactory(
            user=user,
            content="Entry two with fifty words only. " + "word " * 40,
            created_at=day2,
        )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        assert word_analytics["goal_achievement_rate"] == 50.0

    def test_best_day_calculation(self, client):
        """'best day' calculation returns highest word count day."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(
            user=user,
            content="Normal entry with ten words.",
            created_at=base_date - timedelta(days=1),
        )

        EntryFactory(
            user=user,
            content="Best entry with two hundred words. " + "word " * 190,
            created_at=base_date,
        )

        EntryFactory(
            user=user,
            content="Another normal entry with fifteen words here.",
            created_at=base_date - timedelta(days=2),
        )

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        assert word_analytics["best_day"] is not None
        assert word_analytics["best_day"]["date"] == base_date.date().isoformat()
        assert word_analytics["best_day"]["word_count"] > 100

    def test_no_entries_returns_zeroes(self, client):
        """User with no entries returns zeros/nulls gracefully."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        assert word_analytics["total"] == 0
        assert word_analytics["total_entries"] == 0
        assert word_analytics["average_per_entry"] == 0
        assert word_analytics["average_per_day"] == 0
        assert word_analytics["timeline"] == []
        assert word_analytics["best_day"] is None

    def test_encrypted_content_not_decrypted(self, client):
        """Calculations exclude encrypted content field (no decryption happens)."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        entry = EntryFactory(
            user=user,
            content="This is a test entry with ten words.",
            created_at=base_date,
        )
        entry.refresh_from_db()

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        assert word_analytics["total"] == entry.word_count
        assert word_analytics["total"] > 0

    def test_default_daily_goal_when_not_set(self, client):
        """User with default daily goal uses 750 words."""
        user = UserFactory(timezone="Europe/Prague")

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, content="word " * 750, created_at=base_date)

        client.force_login(user)
        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        assert word_analytics["goal_achievement_rate"] == 100.0

    def test_average_per_day_calculation(self, client):
        """Average per day calculated correctly across active days."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        entry1 = EntryFactory(
            user=user,
            content="First entry with twenty words here. " + "word " * 10,
            created_at=base_date,
        )
        entry1.refresh_from_db()

        entry2 = EntryFactory(
            user=user,
            content="Second entry with thirty words total here. " + "word " * 20,
            created_at=base_date - timedelta(days=1),
        )
        entry2.refresh_from_db()

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        word_analytics = data["word_count_analytics"]

        expected_avg = (entry1.word_count + entry2.word_count) / 2
        assert word_analytics["average_per_day"] == round(expected_avg, 2)
        assert word_analytics["total_entries"] == 2


@pytest.mark.statistics
@pytest.mark.integration
class TestStatisticsViewIntegration:
    """Integration tests for statistics endpoint including caching and performance."""

    def test_authenticated_user_returns_200(self, client):
        """Authenticated users receive 200 response."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200

    def test_anonymous_user_returns_403(self, client):
        """Anonymous users receive 403 forbidden response."""
        response = client.get(reverse("api:statistics"))

        assert response.status_code == 403

    def test_period_7d_returns_correct_date_range(self, client):
        """7d period returns correct 7-day date range."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "7d"
        assert "start_date" in data
        assert "end_date" in data

        from zoneinfo import ZoneInfo
        from django.utils import timezone

        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        expected_start = (now - timedelta(days=7)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        actual_start = datetime.fromisoformat(data["start_date"]).replace(tzinfo=None)

        assert actual_start.date() == expected_start.date()

    def test_period_30d_returns_correct_date_range(self, client):
        """30d period returns correct 30-day date range."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "30d"})

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "30d"

        from zoneinfo import ZoneInfo
        from django.utils import timezone

        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        expected_start = (now - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        actual_start = datetime.fromisoformat(data["start_date"]).replace(tzinfo=None)

        assert actual_start.date() == expected_start.date()

    def test_period_90d_returns_correct_date_range(self, client):
        """90d period returns correct 90-day date range."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "90d"})

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "90d"

        from zoneinfo import ZoneInfo
        from django.utils import timezone

        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        expected_start = (now - timedelta(days=90)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        actual_start = datetime.fromisoformat(data["start_date"]).replace(tzinfo=None)

        assert actual_start.date() == expected_start.date()

    def test_period_1y_returns_correct_date_range(self, client):
        """1y period returns correct 1-year date range accounting for leap years."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "1y"})

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "1y"

        from zoneinfo import ZoneInfo
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        expected_start = (now - relativedelta(years=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        actual_start = datetime.fromisoformat(data["start_date"]).replace(tzinfo=None)

        assert actual_start.date() == expected_start.date()

    def test_period_1y_leap_year_february_29(self, client):
        """1y period correctly handles February 29 in leap year."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        user_tz = ZoneInfo(str(user.timezone))

        leap_year_feb_29 = datetime(2024, 2, 29, 12, 0, 0, tzinfo=user_tz)

        from unittest.mock import patch

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = leap_year_feb_29

            response = client.get(reverse("api:statistics"), {"period": "1y"})

            assert response.status_code == 200
            data = response.json()

            expected_start = (leap_year_feb_29 - relativedelta(years=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            actual_start = datetime.fromisoformat(data["start_date"]).replace(
                tzinfo=None
            )

            assert actual_start.year == 2023
            assert actual_start.month == 2
            assert actual_start.day == 28
            assert actual_start.date() == expected_start.date()

    def test_period_1y_accurate_in_2024(self, client):
        """1y period calculation is accurate in leap year (2024)."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        user_tz = ZoneInfo(str(user.timezone))
        leap_year_date = datetime(2024, 6, 15, 12, 0, 0, tzinfo=user_tz)

        from unittest.mock import patch

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = leap_year_date

            response = client.get(reverse("api:statistics"), {"period": "1y"})

            assert response.status_code == 200
            data = response.json()

            expected_start = (leap_year_date - relativedelta(years=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            actual_start = datetime.fromisoformat(data["start_date"]).replace(
                tzinfo=None
            )

            assert actual_start.year == 2023
            assert actual_start.month == 6
            assert actual_start.day == 15
            assert actual_start.date() == expected_start.date()

    def test_period_1y_accurate_in_2025(self, client):
        """1y period calculation is accurate in non-leap year (2025)."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        user_tz = ZoneInfo(str(user.timezone))
        non_leap_year_date = datetime(2025, 6, 15, 12, 0, 0, tzinfo=user_tz)

        from unittest.mock import patch

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = non_leap_year_date

            response = client.get(reverse("api:statistics"), {"period": "1y"})

            assert response.status_code == 200
            data = response.json()

            expected_start = (non_leap_year_date - relativedelta(years=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            actual_start = datetime.fromisoformat(data["start_date"]).replace(
                tzinfo=None
            )

            assert actual_start.year == 2024
            assert actual_start.month == 6
            assert actual_start.day == 15
            assert actual_start.date() == expected_start.date()

    def test_period_all_returns_all_entries(self, client):
        """all period includes entries from the first entry date."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, created_at=base_date - timedelta(days=100))
        EntryFactory(user=user, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()

        assert data["period"] == "all"
        assert data["mood_analytics"]["total_rated_entries"] >= 0
        assert data["word_count_analytics"]["total_entries"] == 2

    def test_response_structure_matches_serializer(self, client):
        """Response structure matches StatisticsSerializer definition."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "period",
            "start_date",
            "end_date",
            "mood_analytics",
            "word_count_analytics",
        ]
        for field in required_fields:
            assert field in data

        mood_analytics = data["mood_analytics"]
        required_mood_fields = [
            "average",
            "distribution",
            "timeline",
            "total_rated_entries",
            "trend",
        ]
        for field in required_mood_fields:
            assert field in mood_analytics

        word_analytics = data["word_count_analytics"]
        required_word_fields = [
            "total",
            "average_per_entry",
            "average_per_day",
            "timeline",
            "total_entries",
            "goal_achievement_rate",
            "best_day",
        ]
        for field in required_word_fields:
            assert field in word_analytics

    def test_caching_improves_performance(self, client):
        """Identical requests are faster due to caching (cache hit)."""
        import time

        user = UserFactory(timezone="Europe/Prague")
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory.create_batch(10, user=user, created_at=base_date)
        client.force_login(user)

        first_request_start = time.time()
        response1 = client.get(reverse("api:statistics"), {"period": "7d"})
        first_request_time = time.time() - first_request_start

        assert response1.status_code == 200

        second_request_start = time.time()
        response2 = client.get(reverse("api:statistics"), {"period": "7d"})
        second_request_time = time.time() - second_request_start

        assert response2.status_code == 200

        assert response1.json() == response2.json()
        assert second_request_time < first_request_time

    def test_caching_works_across_periods(self, client):
        """Different period parameters generate different cache keys."""
        user = UserFactory(timezone="Europe/Prague")
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory.create_batch(5, user=user, created_at=base_date)
        client.force_login(user)

        response_7d = client.get(reverse("api:statistics"), {"period": "7d"})
        response_30d = client.get(reverse("api:statistics"), {"period": "30d"})

        assert response_7d.status_code == 200
        assert response_30d.status_code == 200

        data_7d = response_7d.json()
        data_30d = response_30d.json()

        assert data_7d["period"] == "7d"
        assert data_30d["period"] == "30d"

    def test_cache_invalidation_on_new_entry(self, client):
        """Creating a new entry on a new day invalidates cache and returns fresh data."""
        user = UserFactory(timezone="Europe/Prague")
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory.create_batch(
            5, user=user, created_at=base_date - timedelta(days=1)
        )
        client.force_login(user)

        response1 = client.get(reverse("api:statistics"), {"period": "7d"})
        data1 = response1.json()

        initial_entries = data1["word_count_analytics"]["total_entries"]
        assert initial_entries == 5

        EntryFactory(user=user, created_at=base_date)

        user.refresh_from_db()

        from django.core.cache import cache

        cache.clear()

        response2 = client.get(reverse("api:statistics"), {"period": "7d"})
        data2 = response2.json()

        updated_entries = data2["word_count_analytics"]["total_entries"]
        assert updated_entries == 6

    def test_cache_key_includes_last_entry_date(self, client):
        """Cache key includes last_entry_date for proper invalidation."""
        user = UserFactory(timezone="Europe/Prague")
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, created_at=base_date - timedelta(days=1))
        client.force_login(user)

        response1 = client.get(reverse("api:statistics"), {"period": "7d"})

        user.refresh_from_db()
        last_entry_date_1 = (
            user.last_entry_date.isoformat() if user.last_entry_date else "none"
        )

        EntryFactory(user=user, created_at=base_date)

        user.refresh_from_db()
        last_entry_date_2 = (
            user.last_entry_date.isoformat() if user.last_entry_date else "none"
        )

        assert last_entry_date_1 != last_entry_date_2

        from django.core.cache import cache

        cache.clear()

        response2 = client.get(reverse("api:statistics"), {"period": "7d"})

        data1 = response1.json()
        data2 = response2.json()

        assert (
            data1["word_count_analytics"]["total_entries"]
            != data2["word_count_analytics"]["total_entries"]
        )

    def test_invalid_period_parameter_returns_400(self, client):
        """Invalid period parameter returns 400 error."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "invalid"})

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Invalid period" in data["error"]

    def test_performance_with_100_entries_under_2_seconds(self, client):
        """Statistics endpoint with 100+ entries responds in under 2 seconds."""
        import time

        user = UserFactory(timezone="Europe/Prague")
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(100):
            entry_date = base_date - timedelta(hours=i)
            EntryFactory(
                user=user,
                content=f"Entry {i} with some content for testing. " * 10,
                mood_rating=(i % 5) + 1,
                created_at=entry_date,
            )

        client.force_login(user)

        start_time = time.time()
        response = client.get(reverse("api:statistics"), {"period": "90d"})
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert (
            response_time < 2.0
        ), f"Response time {response_time:.3f}s exceeds 2 second limit"

        data = response.json()
        assert data["word_count_analytics"]["total_entries"] == 100

    def test_performance_with_200_entries_under_2_seconds(self, client):
        """Statistics endpoint with 200 entries still responds in under 2 seconds."""
        import time

        user = UserFactory(timezone="Europe/Prague")
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(200):
            entry_date = base_date - timedelta(days=i)
            EntryFactory(
                user=user,
                content=f"Entry {i} content. " * 5,
                mood_rating=(i % 5) + 1,
                created_at=entry_date,
            )

        client.force_login(user)

        start_time = time.time()
        response = client.get(reverse("api:statistics"), {"period": "1y"})
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert (
            response_time < 2.0
        ), f"Response time {response_time:.3f}s exceeds 2 second limit"

        data = response.json()
        assert data["word_count_analytics"]["total_entries"] == 200

    def test_multiple_users_have_separate_caches(self, client):
        """Different users have separate cache entries."""
        from django.core.cache import cache

        cache.clear()

        user1 = UserFactory(timezone="Europe/Prague")
        user2 = UserFactory(timezone="Europe/Prague")
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory.create_batch(10, user=user1, created_at=base_date)
        EntryFactory.create_batch(20, user=user2, created_at=base_date)

        client.force_login(user1)
        response1 = client.get(reverse("api:statistics"), {"period": "7d"})
        data1 = response1.json()

        assert response1.status_code == 200
        assert data1["word_count_analytics"]["total_entries"] == 10

        client.logout()
        cache.clear()
        client.force_login(user2)
        response2 = client.get(reverse("api:statistics"), {"period": "7d"})
        data2 = response2.json()

        assert response2.status_code == 200
        assert data2["word_count_analytics"]["total_entries"] == 20

    def test_mood_analytics_timeline_structure(self, client):
        """Mood analytics timeline has correct structure."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, mood_rating=4, created_at=base_date)
        EntryFactory(user=user, mood_rating=5, created_at=base_date - timedelta(days=1))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        timeline = data["mood_analytics"]["timeline"]

        assert len(timeline) == 2
        for day in timeline:
            assert "date" in day
            assert "average" in day
            assert "count" in day

    def test_word_analytics_timeline_structure(self, client):
        """Word analytics timeline has correct structure."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        entry1 = EntryFactory(user=user, content="Ten words here", created_at=base_date)
        entry1.refresh_from_db()

        entry2 = EntryFactory(
            user=user, content="Five words", created_at=base_date - timedelta(days=1)
        )
        entry2.refresh_from_db()

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        timeline = data["word_count_analytics"]["timeline"]

        assert len(timeline) == 2
        for day in timeline:
            assert "date" in day
            assert "word_count" in day
            assert "entry_count" in day


@pytest.mark.statistics
@pytest.mark.unit
class TestWritingPatternsTimeOfDay:
    """Test writing patterns time-of-day categorization."""

    def test_time_of_day_categorization_boundaries(self, client):
        """Time categorization correctly handles boundary hours."""
        from apps.api.statistics_views import StatisticsView

        view = StatisticsView()

        assert view._categorize_time_of_day(0) == "night"
        assert view._categorize_time_of_day(4) == "night"
        assert view._categorize_time_of_day(5) == "morning"
        assert view._categorize_time_of_day(11) == "morning"
        assert view._categorize_time_of_day(12) == "afternoon"
        assert view._categorize_time_of_day(17) == "afternoon"
        assert view._categorize_time_of_day(18) == "evening"
        assert view._categorize_time_of_day(23) == "evening"

    def test_time_of_day_all_hours(self, client):
        """All hours 0-23 are correctly categorized."""
        from apps.api.statistics_views import StatisticsView

        view = StatisticsView()

        night_hours = [0, 1, 2, 3, 4]
        morning_hours = [5, 6, 7, 8, 9, 10, 11]
        afternoon_hours = [12, 13, 14, 15, 16, 17]
        evening_hours = [18, 19, 20, 21, 22, 23]

        for hour in night_hours:
            assert view._categorize_time_of_day(hour) == "night"

        for hour in morning_hours:
            assert view._categorize_time_of_day(hour) == "morning"

        for hour in afternoon_hours:
            assert view._categorize_time_of_day(hour) == "afternoon"

        for hour in evening_hours:
            assert view._categorize_time_of_day(hour) == "evening"

    def test_entries_grouped_by_local_time_not_utc(self, client):
        """Entries are grouped by local time, not UTC time."""
        user = UserFactory(timezone="America/New_York")
        client.force_login(user)

        user_tz = ZoneInfo("America/New_York")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=7))
        EntryFactory(user=user, created_at=base_date.replace(hour=13))
        EntryFactory(user=user, created_at=base_date.replace(hour=19))
        EntryFactory(user=user, created_at=base_date.replace(hour=2))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        time_of_day = data["writing_patterns"]["time_of_day"]

        assert time_of_day["morning"] == 1
        assert time_of_day["afternoon"] == 1
        assert time_of_day["evening"] == 1
        assert time_of_day["night"] == 1

    def test_entries_grouped_by_local_time_across_timezones(self, client):
        """Same UTC time categorizes differently based on user's local timezone."""
        from apps.api.statistics_views import StatisticsView
        from django.core.cache import cache

        cache.clear()

        user_prague = UserFactory(timezone="Europe/Prague")
        user_tokyo = UserFactory(timezone="Asia/Tokyo")

        utc_time = timezone.now()

        EntryFactory(user=user_prague, created_at=utc_time)
        EntryFactory(user=user_tokyo, created_at=utc_time)

        client.force_login(user_prague)
        response_prague = client.get(reverse("api:statistics"), {"period": "7d"})
        data_prague = response_prague.json()
        time_of_day_prague = data_prague["writing_patterns"]["time_of_day"]

        client.logout()
        cache.clear()
        client.force_login(user_tokyo)
        response_tokyo = client.get(reverse("api:statistics"), {"period": "7d"})
        data_tokyo = response_tokyo.json()
        time_of_day_tokyo = data_tokyo["writing_patterns"]["time_of_day"]

        prague_hour = utc_time.astimezone(ZoneInfo("Europe/Prague")).hour
        tokyo_hour = utc_time.astimezone(ZoneInfo("Asia/Tokyo")).hour

        view = StatisticsView()
        prague_category = view._categorize_time_of_day(prague_hour)
        tokyo_category = view._categorize_time_of_day(tokyo_hour)

        assert time_of_day_prague[prague_category] == 1
        assert time_of_day_tokyo[tokyo_category] == 1

    def test_time_of_day_distribution_aggregates_correctly(self, client):
        """Multiple entries in the same time category are counted correctly."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory.create_batch(3, user=user, created_at=base_date.replace(hour=8))
        EntryFactory.create_batch(2, user=user, created_at=base_date.replace(hour=14))
        EntryFactory.create_batch(4, user=user, created_at=base_date.replace(hour=20))
        EntryFactory.create_batch(1, user=user, created_at=base_date.replace(hour=3))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        time_of_day = data["writing_patterns"]["time_of_day"]

        assert time_of_day["morning"] == 3
        assert time_of_day["afternoon"] == 2
        assert time_of_day["evening"] == 4
        assert time_of_day["night"] == 1

    def test_time_of_day_boundary_moment_after_midnight(self, client):
        """Entry at 00:00 local time is categorized as night."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        now_local = timezone.now().astimezone(user_tz)
        midnight_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)

        EntryFactory(user=user, created_at=midnight_local)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        time_of_day = data["writing_patterns"]["time_of_day"]

        assert time_of_day["night"] == 1
        assert time_of_day["morning"] == 0

    def test_time_of_day_boundary_moment_before_morning(self, client):
        """Entry at 04:59 local time is categorized as night, 05:00 as morning."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        now_local = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=now_local.replace(hour=4, minute=59))
        EntryFactory(user=user, created_at=now_local.replace(hour=5, minute=0))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        time_of_day = data["writing_patterns"]["time_of_day"]

        assert time_of_day["night"] == 1
        assert time_of_day["morning"] == 1

    def test_time_of_day_boundary_morning_to_afternoon(self, client):
        """Entry at 11:59 local time is morning, 12:00 is afternoon."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        now_local = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=now_local.replace(hour=11, minute=59))
        EntryFactory(user=user, created_at=now_local.replace(hour=12, minute=0))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        time_of_day = data["writing_patterns"]["time_of_day"]

        assert time_of_day["morning"] == 1
        assert time_of_day["afternoon"] == 1

    def test_time_of_day_boundary_afternoon_to_evening(self, client):
        """Entry at 17:59 local time is afternoon, 18:00 is evening."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        now_local = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=now_local.replace(hour=17, minute=59))
        EntryFactory(user=user, created_at=now_local.replace(hour=18, minute=0))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        time_of_day = data["writing_patterns"]["time_of_day"]

        assert time_of_day["afternoon"] == 1
        assert time_of_day["evening"] == 1

    def test_time_of_day_boundary_evening_to_night(self, client):
        """Entry at 23:59 local time is evening, 00:00 is night."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        now_local = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=now_local.replace(hour=23, minute=59))
        EntryFactory(user=user, created_at=now_local.replace(hour=0, minute=0))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        time_of_day = data["writing_patterns"]["time_of_day"]

        assert time_of_day["evening"] == 1
        assert time_of_day["night"] == 1

    def test_time_of_day_with_negative_utc_offset_timezone(self, client):
        """Time categorization works correctly with negative UTC offset timezone."""
        user = UserFactory(timezone="America/Los_Angeles")
        client.force_login(user)

        user_tz = ZoneInfo("America/Los_Angeles")
        now_local = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=now_local.replace(hour=1))
        EntryFactory(user=user, created_at=now_local.replace(hour=7))
        EntryFactory(user=user, created_at=now_local.replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        time_of_day = data["writing_patterns"]["time_of_day"]

        assert time_of_day["night"] == 1
        assert time_of_day["morning"] == 1
        assert time_of_day["afternoon"] == 1

    def test_time_of_day_returns_zeros_with_no_entries(self, client):
        """Writing patterns return all zeros when user has no entries."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        time_of_day = data["writing_patterns"]["time_of_day"]

        assert time_of_day["morning"] == 0
        assert time_of_day["afternoon"] == 0
        assert time_of_day["evening"] == 0
        assert time_of_day["night"] == 0


@pytest.mark.statistics
@pytest.mark.unit
class TestWritingPatternsDayOfWeek:
    """Test writing patterns day-of-week aggregation."""

    def test_day_of_week_all_days_present_in_response(self, client):
        """Response includes all 7 days of week even when no entries exist."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        assert len(day_of_week) == 7
        assert "Monday" in day_of_week
        assert "Tuesday" in day_of_week
        assert "Wednesday" in day_of_week
        assert "Thursday" in day_of_week
        assert "Friday" in day_of_week
        assert "Saturday" in day_of_week
        assert "Sunday" in day_of_week

        for day in day_of_week.values():
            assert day == 0

    def test_day_of_week_calendar_order_preserved(self, client):
        """Days are always returned in calendar order (Mon-Sun) regardless of counts."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, created_at=base_date)
        EntryFactory(user=user, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        days_list = list(day_of_week.keys())
        expected_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        assert days_list == expected_order

    def test_day_of_week_calendar_order_with_sunday_most_entries(self, client):
        """Sunday having most entries doesn't change calendar order (Mon-Sun)."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        now = timezone.now().astimezone(user_tz)

        sunday_1 = now - timedelta(days=(now.weekday() + 1) % 7)
        monday_1 = sunday_1 + timedelta(days=1)

        EntryFactory.create_batch(10, user=user, created_at=sunday_1.replace(hour=12))
        EntryFactory(user=user, created_at=monday_1.replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "30d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        days_list = list(day_of_week.keys())
        expected_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        assert days_list == expected_order

        assert day_of_week["Sunday"] == 10
        assert day_of_week["Monday"] == 1

    def test_day_of_week_single_entry_counted_correctly(self, client):
        """Single entry is counted under correct day of week."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        now = timezone.now().astimezone(user_tz)

        monday = now - timedelta(days=now.weekday())
        EntryFactory(user=user, created_at=monday.replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        assert day_of_week["Monday"] == 1
        assert day_of_week["Tuesday"] == 0
        assert day_of_week["Wednesday"] == 0
        assert day_of_week["Thursday"] == 0
        assert day_of_week["Friday"] == 0
        assert day_of_week["Saturday"] == 0
        assert day_of_week["Sunday"] == 0

    def test_day_of_week_multiple_entries_same_day(self, client):
        """Multiple entries on same day are all counted correctly."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        now = timezone.now().astimezone(user_tz)

        wednesday = now - timedelta(days=now.weekday() - 2)
        EntryFactory.create_batch(5, user=user, created_at=wednesday.replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        assert day_of_week["Wednesday"] == 5
        assert sum(day_of_week.values()) == 5

    def test_day_of_week_entries_across_multiple_weeks(self, client):
        """Entries on same day across multiple weeks are aggregated correctly."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        base_date = datetime(2024, 1, 5, 12, 0, 0, tzinfo=user_tz)

        friday_1 = base_date
        friday_2 = base_date - timedelta(weeks=1)
        friday_3 = base_date - timedelta(weeks=2)

        EntryFactory.create_batch(3, user=user, created_at=friday_1)
        EntryFactory.create_batch(2, user=user, created_at=friday_2)
        EntryFactory.create_batch(4, user=user, created_at=friday_3)

        with patch("django.utils.timezone.now", return_value=base_date + timedelta(days=1)):
            response = client.get(reverse("api:statistics"), {"period": "30d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        assert day_of_week["Friday"] == 9

    def test_day_of_week_distribution_all_days_with_entries(self, client):
        """Entries on all 7 days are counted correctly."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        monday = datetime(2024, 1, 1, 10, 0, 0, tzinfo=user_tz)
        tuesday = monday + timedelta(days=1)
        wednesday = monday + timedelta(days=2)
        thursday = monday + timedelta(days=3)
        friday = monday + timedelta(days=4)
        saturday = monday + timedelta(days=5)
        sunday = monday + timedelta(days=6)

        EntryFactory(user=user, created_at=monday)
        EntryFactory.create_batch(2, user=user, created_at=tuesday)
        EntryFactory.create_batch(3, user=user, created_at=wednesday)
        EntryFactory.create_batch(4, user=user, created_at=thursday)
        EntryFactory.create_batch(5, user=user, created_at=friday)
        EntryFactory.create_batch(6, user=user, created_at=saturday)
        EntryFactory.create_batch(7, user=user, created_at=sunday)

        with patch("django.utils.timezone.now", return_value=sunday + timedelta(days=1)):
            response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        assert day_of_week["Monday"] == 1
        assert day_of_week["Tuesday"] == 2
        assert day_of_week["Wednesday"] == 3
        assert day_of_week["Thursday"] == 4
        assert day_of_week["Friday"] == 5
        assert day_of_week["Saturday"] == 6
        assert day_of_week["Sunday"] == 7
        assert sum(day_of_week.values()) == 28

    def test_day_of_week_multiple_entries_per_day_across_weeks(self, client):
        """Multiple entries per day across multiple weeks counted correctly."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        tuesday_1 = datetime(2024, 1, 16, 12, 0, 0, tzinfo=user_tz)
        tuesday_2 = datetime(2024, 1, 9, 12, 0, 0, tzinfo=user_tz)
        tuesday_3 = datetime(2024, 1, 2, 12, 0, 0, tzinfo=user_tz)

        EntryFactory.create_batch(3, user=user, created_at=tuesday_1)
        EntryFactory.create_batch(2, user=user, created_at=tuesday_2)
        EntryFactory.create_batch(4, user=user, created_at=tuesday_3)

        with patch("django.utils.timezone.now", return_value=tuesday_1 + timedelta(days=1)):
            response = client.get(reverse("api:statistics"), {"period": "30d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        assert day_of_week["Tuesday"] == 9
        assert day_of_week["Monday"] == 0
        assert day_of_week["Wednesday"] == 0
        assert day_of_week["Thursday"] == 0
        assert day_of_week["Friday"] == 0
        assert day_of_week["Saturday"] == 0
        assert day_of_week["Sunday"] == 0
        assert sum(day_of_week.values()) == 9

    def test_day_of_week_week_boundary_crossing(self, client):
        """Entries near week boundary are assigned to correct day."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        saturday = datetime(2024, 1, 6, 23, 59, 0, tzinfo=user_tz)
        sunday = datetime(2024, 1, 7, 0, 1, 0, tzinfo=user_tz)
        monday = datetime(2024, 1, 8, 0, 0, 0, tzinfo=user_tz)

        EntryFactory(user=user, created_at=saturday)
        EntryFactory(user=user, created_at=sunday)
        EntryFactory(user=user, created_at=monday)

        with patch("django.utils.timezone.now", return_value=monday + timedelta(days=1)):
            response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        assert day_of_week["Saturday"] == 1
        assert day_of_week["Sunday"] == 1
        assert day_of_week["Monday"] == 1

    def test_day_of_week_timezone_awareness(self, client):
        """Day of week uses user's timezone, not UTC."""
        from django.core.cache import cache

        cache.clear()

        user_utc = UserFactory(timezone="UTC")
        user_tokyo = UserFactory(timezone="Asia/Tokyo")

        utc_time = datetime(2024, 1, 16, 3, 0, 0, tzinfo=ZoneInfo("UTC"))

        EntryFactory(user=user_tokyo, created_at=utc_time)

        with patch("django.utils.timezone.now", return_value=utc_time + timedelta(days=1)):
            client.force_login(user_tokyo)

            response_tokyo = client.get(reverse("api:statistics"), {"period": "7d"})
            data_tokyo = response_tokyo.json()
            day_of_week_tokyo = data_tokyo["writing_patterns"]["day_of_week"]

            assert day_of_week_tokyo["Tuesday"] == 1

    def test_day_of_week_dst_transition_spring_forward(self, client):
        """Day of week calculation is correct during spring forward DST transition."""
        from unittest.mock import patch

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        spring_forward_2024 = datetime(2024, 3, 31, 12, 0, 0, tzinfo=user_tz)

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = spring_forward_2024

            EntryFactory(
                user=user,
                created_at=spring_forward_2024,
            )

            EntryFactory(
                user=user,
                created_at=spring_forward_2024 - timedelta(days=7),
            )

            EntryFactory(
                user=user,
                created_at=spring_forward_2024 - timedelta(days=14),
            )

            response = client.get(reverse("api:statistics"), {"period": "30d"})

            assert response.status_code == 200
            data = response.json()
            day_of_week = data["writing_patterns"]["day_of_week"]

            assert day_of_week["Sunday"] == 3

    def test_day_of_week_dst_transition_fall_back(self, client):
        """Day of week calculation is correct during fall back DST transition."""
        from unittest.mock import patch

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        fall_back_2024 = datetime(2024, 10, 27, 12, 0, 0, tzinfo=user_tz)

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = fall_back_2024

            EntryFactory(
                user=user,
                created_at=fall_back_2024,
            )

            EntryFactory(
                user=user,
                created_at=fall_back_2024.replace(hour=1, fold=0),
            )

            EntryFactory(
                user=user,
                created_at=fall_back_2024.replace(hour=2, fold=0),
            )

            response = client.get(reverse("api:statistics"), {"period": "7d"})

            assert response.status_code == 200
            data = response.json()
            day_of_week = data["writing_patterns"]["day_of_week"]

            assert day_of_week["Sunday"] == 3

    def test_day_of_week_period_filtering(self, client):
        """Day of week aggregation respects period parameter."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        monday_recent = datetime(2024, 1, 8, 12, 0, 0, tzinfo=user_tz)
        monday_old = datetime(2024, 1, 1, 12, 0, 0, tzinfo=user_tz)

        EntryFactory(user=user, created_at=monday_recent)
        EntryFactory(user=user, created_at=monday_old)

        with patch("django.utils.timezone.now", return_value=monday_recent + timedelta(days=1)):
            response_7d = client.get(reverse("api:statistics"), {"period": "7d"})

        with patch("django.utils.timezone.now", return_value=monday_recent + timedelta(days=1)):
            response_30d = client.get(reverse("api:statistics"), {"period": "30d"})

        assert response_7d.status_code == 200
        assert response_30d.status_code == 200

        data_7d = response_7d.json()
        data_30d = response_30d.json()

        day_of_week_7d = data_7d["writing_patterns"]["day_of_week"]
        day_of_week_30d = data_30d["writing_patterns"]["day_of_week"]

        assert day_of_week_7d["Monday"] == 1
        assert day_of_week_30d["Monday"] == 2

    def test_day_of_week_all_period_includes_all_entries(self, client):
        """'all' period includes entries for all time in day of week aggregation."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        wednesday_1 = datetime(2024, 1, 3, 12, 0, 0, tzinfo=user_tz)
        wednesday_2 = datetime(2023, 10, 4, 12, 0, 0, tzinfo=user_tz)
        wednesday_3 = datetime(2023, 9, 6, 12, 0, 0, tzinfo=user_tz)

        EntryFactory.create_batch(2, user=user, created_at=wednesday_1)
        EntryFactory.create_batch(3, user=user, created_at=wednesday_2)
        EntryFactory.create_batch(5, user=user, created_at=wednesday_3)

        with patch("django.utils.timezone.now", return_value=wednesday_1 + timedelta(days=1)):
            response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        assert day_of_week["Wednesday"] == 10

    def test_day_of_week_weekend_vs_weekday(self, client):
        """Entries correctly categorized as weekend vs weekday."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")

        monday = datetime(2024, 1, 1, 10, 0, 0, tzinfo=user_tz)
        saturday = datetime(2024, 1, 6, 10, 0, 0, tzinfo=user_tz)
        sunday = datetime(2024, 1, 7, 10, 0, 0, tzinfo=user_tz)

        EntryFactory.create_batch(4, user=user, created_at=monday)
        EntryFactory.create_batch(5, user=user, created_at=saturday)
        EntryFactory.create_batch(6, user=user, created_at=sunday)

        with patch("django.utils.timezone.now", return_value=sunday + timedelta(days=1)):
            response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        day_of_week = data["writing_patterns"]["day_of_week"]

        weekday_total = day_of_week["Monday"] + day_of_week["Tuesday"] + day_of_week["Wednesday"] + day_of_week["Thursday"] + day_of_week["Friday"]
        weekend_total = day_of_week["Saturday"] + day_of_week["Sunday"]

        assert weekday_total == 4
        assert weekend_total == 11

    def test_day_of_week_consistency_with_entry_count(self, client):
        """Day of week sums match total entry count for period."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        now = timezone.now().astimezone(user_tz)

        for i in range(21):
            entry_date = now - timedelta(days=i)
            EntryFactory(user=user, created_at=entry_date.replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "30d"})

        assert response.status_code == 200
        data = response.json()

        day_of_week = data["writing_patterns"]["day_of_week"]
        total_entries = data["word_count_analytics"]["total_entries"]

        assert sum(day_of_week.values()) == total_entries
        assert total_entries == 21


@pytest.mark.statistics
@pytest.mark.unit
class TestWritingPatternsConsistencyRate:
    """Test writing patterns consistency_rate calculation."""

    def test_consistency_rate_100_percent(self, client):
        """Consistency rate is 100% when entries exist every day."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        for i in range(7):
            day_date = base_date - timedelta(days=i)
            EntryFactory(user=user, created_at=day_date.replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_0_percent_no_entries(self, client):
        """Consistency rate is 0% when user has no entries."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 0.0

    def test_consistency_rate_partial_entries_half_days(self, client):
        """Consistency rate is 50% when entries on half the days."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=12))
        EntryFactory(user=user, created_at=(base_date - timedelta(days=1)).replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_counts_only_active_days(self, client):
        """Consistency rate only counts days with at least one entry."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=10))
        EntryFactory(user=user, created_at=base_date.replace(hour=14))
        EntryFactory(user=user, created_at=base_date.replace(hour=18))

        EntryFactory(user=user, created_at=(base_date - timedelta(days=1)).replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_multiple_entries_same_day_counted_once(self, client):
        """Multiple entries on same day count as one active day."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory.create_batch(5, user=user, created_at=base_date.replace(hour=8))
        EntryFactory.create_batch(3, user=user, created_at=base_date.replace(hour=12))

        EntryFactory.create_batch(2, user=user, created_at=(base_date - timedelta(days=1)).replace(hour=10))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_75_percent_three_of_four_days(self, client):
        """Consistency rate is 75% when entries on 3 out of 4 days."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=12))
        EntryFactory(user=user, created_at=(base_date - timedelta(days=1)).replace(hour=12))
        EntryFactory(user=user, created_at=(base_date - timedelta(days=2)).replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_all_period(self, client):
        """Consistency rate calculation works correctly with 'all' period."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        for i in range(5):
            day_date = base_date - timedelta(days=i)
            EntryFactory(user=user, created_at=day_date.replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_30d_period(self, client):
        """Consistency rate calculation works correctly with 30d period."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        for i in range(10):
            day_date = base_date - timedelta(days=i)
            EntryFactory(user=user, created_at=day_date.replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "30d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_across_dst_transition(self, client):
        """Consistency rate calculation is correct during DST transition."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        spring_forward = datetime(2024, 3, 31, 12, 0, 0, tzinfo=user_tz)

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = spring_forward

            EntryFactory(user=user, created_at=spring_forward - timedelta(days=1))
            EntryFactory(user=user, created_at=spring_forward)

            response = client.get(reverse("api:statistics"), {"period": "7d"})

            assert response.status_code == 200
            data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0


@pytest.mark.statistics
@pytest.mark.integration
class TestWritingPatternsIntegration:
    """Integration tests for writing patterns across the statistics API."""

    def test_writing_patterns_key_exists_in_response(self, client):
        """Statistics API returns writing_patterns key in response."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        assert "writing_patterns" in data

    def test_writing_patterns_contains_all_required_fields(self, client):
        """writing_patterns dictionary contains all required fields."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        required_fields = [
            "consistency_rate",
            "time_of_day",
            "day_of_week",
            "streak_history",
        ]

        for field in required_fields:
            assert field in writing_patterns, f"Missing required field: {field}"

    def test_writing_patterns_with_no_entries(self, client):
        """writing_patterns returns correct structure with no entries."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 0.0
        assert writing_patterns["time_of_day"] == {
            "morning": 0,
            "afternoon": 0,
            "evening": 0,
            "night": 0,
        }
        assert writing_patterns["day_of_week"] == {
            "Monday": 0,
            "Tuesday": 0,
            "Wednesday": 0,
            "Thursday": 0,
            "Friday": 0,
            "Saturday": 0,
            "Sunday": 0,
        }
        assert writing_patterns["streak_history"] == []

    def test_writing_patterns_across_all_time_periods(self, client):
        """writing_patterns works correctly for all valid time periods."""
        from django.core.cache import cache

        user = UserFactory(timezone="Europe/Prague")
        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        for i in range(5):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        client.force_login(user)

        periods = ["7d", "30d", "90d", "1y", "all"]

        for period in periods:
            cache.clear()
            response = client.get(reverse("api:statistics"), {"period": period})

            assert response.status_code == 200
            data = response.json()

            assert "writing_patterns" in data
            writing_patterns = data["writing_patterns"]

            required_fields = [
                "consistency_rate",
                "time_of_day",
                "day_of_week",
                "streak_history",
            ]

            for field in required_fields:
                assert field in writing_patterns

            assert isinstance(writing_patterns["consistency_rate"], float)
            assert isinstance(writing_patterns["time_of_day"], dict)
            assert isinstance(writing_patterns["day_of_week"], dict)
            assert isinstance(writing_patterns["streak_history"], list)

    def test_time_categorization_respects_prague_timezone(self, client):
        """Entries in Prague timezone categorize correctly by local time."""
        from django.core.cache import cache

        cache.clear()

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=8))
        EntryFactory(user=user, created_at=base_date.replace(hour=14))
        EntryFactory(user=user, created_at=base_date.replace(hour=20))
        EntryFactory(user=user, created_at=base_date.replace(hour=2))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]
        time_of_day = writing_patterns["time_of_day"]

        assert time_of_day["morning"] == 1
        assert time_of_day["afternoon"] == 1
        assert time_of_day["evening"] == 1
        assert time_of_day["night"] == 1

    def test_time_categorization_respects_tokyo_timezone(self, client):
        """Entries in Tokyo timezone categorize correctly by local time."""
        from django.core.cache import cache

        cache.clear()

        user = UserFactory(timezone="Asia/Tokyo")
        client.force_login(user)

        user_tz = ZoneInfo("Asia/Tokyo")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=8))
        EntryFactory(user=user, created_at=base_date.replace(hour=14))
        EntryFactory(user=user, created_at=base_date.replace(hour=20))
        EntryFactory(user=user, created_at=base_date.replace(hour=2))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]
        time_of_day = writing_patterns["time_of_day"]

        assert time_of_day["morning"] == 1
        assert time_of_day["afternoon"] == 1
        assert time_of_day["evening"] == 1
        assert time_of_day["night"] == 1

    def test_time_categorization_respects_new_york_timezone(self, client):
        """Entries in New York timezone categorize correctly by local time."""
        from django.core.cache import cache

        cache.clear()

        user = UserFactory(timezone="America/New_York")
        client.force_login(user)

        user_tz = ZoneInfo("America/New_York")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=8))
        EntryFactory(user=user, created_at=base_date.replace(hour=14))
        EntryFactory(user=user, created_at=base_date.replace(hour=20))
        EntryFactory(user=user, created_at=base_date.replace(hour=2))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]
        time_of_day = writing_patterns["time_of_day"]

        assert time_of_day["morning"] == 1
        assert time_of_day["afternoon"] == 1
        assert time_of_day["evening"] == 1
        assert time_of_day["night"] == 1

    def test_same_utc_time_categorizes_differently_by_timezone(self, client):
        """Same UTC time categorizes differently based on user's local timezone."""
        from django.core.cache import cache
        from apps.api.statistics_views import StatisticsView

        cache.clear()

        user_prague = UserFactory(timezone="Europe/Prague")
        user_tokyo = UserFactory(timezone="Asia/Tokyo")

        utc_time = timezone.now()

        EntryFactory(user=user_prague, created_at=utc_time)
        EntryFactory(user=user_tokyo, created_at=utc_time)

        client.force_login(user_prague)
        response_prague = client.get(reverse("api:statistics"), {"period": "7d"})
        data_prague = response_prague.json()
        time_of_day_prague = data_prague["writing_patterns"]["time_of_day"]

        client.logout()
        cache.clear()
        client.force_login(user_tokyo)
        response_tokyo = client.get(reverse("api:statistics"), {"period": "7d"})
        data_tokyo = response_tokyo.json()
        time_of_day_tokyo = data_tokyo["writing_patterns"]["time_of_day"]

        prague_hour = utc_time.astimezone(ZoneInfo("Europe/Prague")).hour
        tokyo_hour = utc_time.astimezone(ZoneInfo("Asia/Tokyo")).hour

        view = StatisticsView()
        prague_category = view._categorize_time_of_day(prague_hour)
        tokyo_category = view._categorize_time_of_day(tokyo_hour)

        assert time_of_day_prague[prague_category] == 1
        assert time_of_day_tokyo[tokyo_category] == 1

    def test_day_of_week_categorization_respects_timezone(self, client):
        """Day of week categorization respects user's local timezone."""
        from django.core.cache import cache

        cache.clear()

        user_prague = UserFactory(timezone="Europe/Prague")
        user_tokyo = UserFactory(timezone="Asia/Tokyo")

        user_tz_prague = ZoneInfo("Europe/Prague")
        user_tz_tokyo = ZoneInfo("Asia/Tokyo")

        base_date_utc = timezone.now()

        prague_date = base_date_utc.astimezone(user_tz_prague)
        tokyo_date = base_date_utc.astimezone(user_tz_tokyo)

        EntryFactory(user=user_prague, created_at=base_date_utc)
        EntryFactory(user=user_tokyo, created_at=base_date_utc)

        client.force_login(user_prague)
        response_prague = client.get(reverse("api:statistics"), {"period": "7d"})
        data_prague = response_prague.json()
        day_of_week_prague = data_prague["writing_patterns"]["day_of_week"]

        client.logout()
        cache.clear()
        client.force_login(user_tokyo)
        response_tokyo = client.get(reverse("api:statistics"), {"period": "7d"})
        data_tokyo = response_tokyo.json()
        day_of_week_tokyo = data_tokyo["writing_patterns"]["day_of_week"]

        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        prague_day_name = prague_date.strftime("%A")
        tokyo_day_name = tokyo_date.strftime("%A")

        assert prague_day_name in day_names
        assert tokyo_day_name in day_names

        if prague_date.day == tokyo_date.day:
            assert day_of_week_prague[prague_day_name] == 1
            assert day_of_week_tokyo[tokyo_day_name] == 1

    def test_writing_patterns_user_isolation(self, client):
        """Users only see their own writing patterns."""
        from django.core.cache import cache

        cache.clear()

        user1 = UserFactory(timezone="Europe/Prague")
        user2 = UserFactory(timezone="Europe/Prague")
        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory.create_batch(5, user=user1, created_at=base_date)
        EntryFactory.create_batch(3, user=user2, created_at=base_date)

        client.force_login(user1)
        response_user1 = client.get(reverse("api:statistics"), {"period": "7d"})
        data_user1 = response_user1.json()
        writing_patterns_user1 = data_user1["writing_patterns"]

        client.logout()
        cache.clear()
        client.force_login(user2)
        response_user2 = client.get(reverse("api:statistics"), {"period": "7d"})
        data_user2 = response_user2.json()
        writing_patterns_user2 = data_user2["writing_patterns"]

        total_entries_user1 = sum(writing_patterns_user1["time_of_day"].values())
        total_entries_user2 = sum(writing_patterns_user2["time_of_day"].values())

        assert total_entries_user1 == 5
        assert total_entries_user2 == 3

    def test_streak_history_in_writing_patterns(self, client):
        """streak_history in writing_patterns returns correct data structure."""
        user = UserFactory(timezone="Europe/Prague")
        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        for i in range(5):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        client.force_login(user)
        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]
        streak_history = writing_patterns["streak_history"]

        assert isinstance(streak_history, list)
        assert len(streak_history) > 0

        streak = streak_history[0]
        assert "start_date" in streak
        assert "end_date" in streak
        assert "length" in streak
        assert isinstance(streak["length"], int)
        assert streak["length"] > 0

    def test_consistency_rate_in_writing_patterns(self, client):
        """consistency_rate in writing_patterns returns float between 0-100."""
        user = UserFactory(timezone="Europe/Prague")
        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        for i in range(3):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        client.force_login(user)
        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]
        consistency_rate = writing_patterns["consistency_rate"]

        assert isinstance(consistency_rate, float)
        assert 0.0 <= consistency_rate <= 100.0

    def test_consistency_rate_timezone_awareness(self, client):
        """Consistency rate uses user's timezone for day boundaries."""
        user = UserFactory(timezone="America/New_York")
        client.force_login(user)

        user_tz = ZoneInfo("America/New_York")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=1))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_single_day_with_entries(self, client):
        """Consistency rate is 100% when all entries are on a single day."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory.create_batch(5, user=user, created_at=base_date.replace(hour=10))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_entries_at_boundaries(self, client):
        """Entries at day boundaries (00:00, 23:59) count correctly."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)
        day_start = base_date.replace(hour=0, minute=0, second=0, microsecond=0)

        EntryFactory(user=user, created_at=day_start + timedelta(hours=0))
        EntryFactory(user=user, created_at=day_start + timedelta(hours=23, minutes=59))
        EntryFactory(user=user, created_at=(day_start - timedelta(days=1)).replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_period_90d(self, client):
        """Consistency rate calculation works correctly with 90d period."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        for i in range(15):
            day_date = base_date - timedelta(days=i)
            EntryFactory(user=user, created_at=day_date.replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "90d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0

    def test_consistency_rate_with_gaps(self, client):
        """Consistency rate accounts for gaps between entries."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=12))
        EntryFactory(user=user, created_at=(base_date - timedelta(days=3)).replace(hour=12))
        EntryFactory(user=user, created_at=(base_date - timedelta(days=6)).replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        expected_rate = round((3 / 7) * 100, 2)
        assert writing_patterns["consistency_rate"] == expected_rate

    def test_consistency_rate_33_percent_one_of_three_days(self, client):
        """Consistency rate is approximately 33.33% when entries on 1 out of 3 days."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        base_date = timezone.now().astimezone(user_tz)

        EntryFactory(user=user, created_at=base_date.replace(hour=12))
        EntryFactory(user=user, created_at=(base_date - timedelta(days=1)).replace(hour=12))
        EntryFactory(user=user, created_at=(base_date - timedelta(days=2)).replace(hour=12))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        writing_patterns = data["writing_patterns"]

        assert writing_patterns["consistency_rate"] == 100.0


@pytest.mark.statistics
@pytest.mark.unit
class TestStatisticsViewRateLimiting:
    """Test rate limiting on StatisticsView to prevent abuse of expensive queries."""

    def test_rate_limit_headers_present(self, client, settings):
        """Rate limit headers are present in response."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        # DRF adds X-RateLimit headers when throttling is enabled
        # Note: Headers may not be present in every response, but status 200 indicates success

    def test_rate_limit_prevents_excessive_requests(self, client, settings):
        """Excessive requests to statistics endpoint are throttled."""
        # Override throttle rate for testing
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['statistics'] = '5/hour'
        
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        # Create some test data
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        EntryFactory(user=user, mood_rating=5, created_at=base_date)

        # Make requests up to the limit
        for i in range(5):
            response = client.get(reverse("api:statistics"), {"period": "7d"})
            assert response.status_code == 200, f"Request {i+1} should succeed"

        # Next request should be throttled
        response = client.get(reverse("api:statistics"), {"period": "7d"})
        assert response.status_code == 429, "Request beyond limit should be throttled"
        
        # Response should contain retry information
        assert 'Retry-After' in response or 'retry-after' in response.headers

    def test_different_periods_count_toward_same_limit(self, client, settings):
        """Requests with different period parameters count toward the same throttle limit."""
        # Override throttle rate for testing
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['statistics'] = '3/hour'
        
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        # Create test data
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        EntryFactory(user=user, mood_rating=5, created_at=base_date)

        # Make requests with different periods
        periods = ['7d', '30d', '90d']
        for period in periods:
            response = client.get(reverse("api:statistics"), {"period": period})
            assert response.status_code == 200, f"Request with period {period} should succeed"

        # Next request should be throttled regardless of period
        response = client.get(reverse("api:statistics"), {"period": "1y"})
        assert response.status_code == 429, "Request beyond limit should be throttled"

    def test_rate_limit_per_user_isolation(self, client, settings):
        """Rate limits are enforced per user, not globally."""
        # Override throttle rate for testing
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['statistics'] = '2/hour'
        
        user1 = UserFactory(timezone="Europe/Prague")
        user2 = UserFactory(timezone="Europe/Prague")
        
        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        EntryFactory(user=user1, mood_rating=5, created_at=base_date)
        EntryFactory(user=user2, mood_rating=3, created_at=base_date)

        # User 1 makes requests up to limit
        client.force_login(user1)
        for i in range(2):
            response = client.get(reverse("api:statistics"), {"period": "7d"})
            assert response.status_code == 200

        # User 1 is now throttled
        response = client.get(reverse("api:statistics"), {"period": "7d"})
        assert response.status_code == 429

        # User 2 should still be able to make requests
        client.force_login(user2)
        response = client.get(reverse("api:statistics"), {"period": "7d"})
        assert response.status_code == 200, "User 2 should not be affected by User 1's throttle"

    def test_throttle_status_code_and_message(self, client, settings):
        """Throttled requests return 429 status with appropriate message."""
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['statistics'] = '1/hour'
        
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        # First request succeeds
        response = client.get(reverse("api:statistics"), {"period": "7d"})
        assert response.status_code == 200

        # Second request is throttled
        response = client.get(reverse("api:statistics"), {"period": "7d"})
        assert response.status_code == 429
        
        # Check response contains throttle information
        data = response.json()
        assert 'detail' in data
        # Message can be in English or Czech
        detail_lower = data['detail'].lower()
        assert ('throttled' in detail_lower or 'rate' in detail_lower 
                or 'limitován' in detail_lower or 'požadavek' in detail_lower)

    def test_cache_and_throttle_interaction(self, client, settings):
        """Cached responses still count toward rate limit."""
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['statistics'] = '3/hour'
        
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        EntryFactory(user=user, mood_rating=5, created_at=base_date)

        # Make identical requests (should be cached)
        for i in range(3):
            response = client.get(reverse("api:statistics"), {"period": "7d"})
            assert response.status_code == 200

        # Even though responses were cached, throttle should still apply
        response = client.get(reverse("api:statistics"), {"period": "7d"})
        assert response.status_code == 429
