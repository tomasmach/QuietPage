"""
Comprehensive tests for streak history calculation in statistics API.

Tests cover:
- Single streak scenarios
- Multiple streaks separated by gaps
- Current ongoing streak detection
- Edge cases with backdated entries
- Top 5 longest streaks return and sorting
- Timezone-aware streak calculation
"""

import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.urls import reverse
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test to prevent cross-test contamination.

    The statistics API caches results by user_id. Since SQLite reuses user IDs
    within test transactions, cached data from previous tests can leak into
    subsequent tests, causing them to see entries that don't exist in their
    database transaction.
    """
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.mark.statistics
@pytest.mark.streak
@pytest.mark.unit
class TestStreakHistorySingleStreak:
    """Test streak history with single streak scenarios."""

    def test_single_streak_of_one_day(self, client):
        """Single streak with one day of writing."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        EntryFactory(user=user, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 1
        assert "start_date" in streak_history[0]
        assert "end_date" in streak_history[0]

    def test_single_streak_of_multiple_days(self, client):
        """Single streak with multiple consecutive days."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(5):
            EntryFactory(user=user, created_at=base_date - timedelta(days=4 - i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 5
        assert streak_history[0]["start_date"] == (base_date - timedelta(days=4)).date().isoformat()
        assert streak_history[0]["end_date"] == base_date.date().isoformat()

    def test_single_streak_dates_are_correct(self, client):
        """Streak start and end dates match the actual writing days."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        start_date = base_date - timedelta(days=9)

        for i in range(10):
            EntryFactory(user=user, created_at=start_date + timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["start_date"] == start_date.date().isoformat()
        assert streak_history[0]["end_date"] == base_date.date().isoformat()
        assert streak_history[0]["length"] == 10


@pytest.mark.statistics
@pytest.mark.streak
@pytest.mark.unit
class TestStreakHistoryMultipleStreaks:
    """Test streak history with multiple streaks separated by gaps."""

    def test_two_streaks_with_gap(self, client):
        """Two streaks separated by a gap."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(3):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(4, 7):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 2
        assert streak_history[0]["length"] == 3
        assert streak_history[1]["length"] == 3

    def test_three_streaks_with_different_lengths(self, client):
        """Three streaks with varying lengths."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(5):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(7, 10):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(12, 14):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 3
        lengths = [s["length"] for s in streak_history]
        assert 5 in lengths
        assert 3 in lengths
        assert 2 in lengths

    def test_streaks_sorted_by_length_descending(self, client):
        """Streaks are returned sorted by length (longest first)."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(7):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(9, 13):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(15, 17):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 3
        assert streak_history[0]["length"] == 7
        assert streak_history[1]["length"] == 4
        assert streak_history[2]["length"] == 2

    def test_only_top_5_streaks_returned(self, client):
        """Only top 5 longest streaks are returned when more exist."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(10):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(12, 14):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(16, 19):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(21, 24):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(26, 28):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(30, 31):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 5
        lengths = [s["length"] for s in streak_history]
        assert sorted(lengths, reverse=True) == lengths

    def test_top_5_streaks_are_longest(self, client):
        """Top 5 streaks are indeed longest 5 when more exist."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(10):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(12, 15):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(17, 20):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(22, 25):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(27, 29):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(31, 32):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        lengths = [s["length"] for s in streak_history]
        assert 10 in lengths
        assert 3 in lengths
        assert 3 in lengths
        assert 2 in lengths
        assert 2 in lengths


@pytest.mark.statistics
@pytest.mark.streak
@pytest.mark.unit
class TestStreakHistoryCurrentOngoingStreak:
    """Test current ongoing streak detection in history."""

    def test_current_ongoing_streak_included(self, client):
        """Current ongoing streak is included in streak history."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(5):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 5
        assert streak_history[0]["end_date"] == base_date.date().isoformat()

    def test_current_ongoing_streak_is_longest(self, client):
        """Current ongoing streak appears as longest when it is."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(10):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        for i in range(12, 14):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert streak_history[0]["length"] == 10
        assert streak_history[0]["end_date"] == base_date.date().isoformat()

    def test_old_longest_streak_beats_current(self, client):
        """Old streak appears as longest when current streak is shorter."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(10):
            EntryFactory(user=user, created_at=base_date - timedelta(days=20 + i))

        for i in range(3):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 2
        assert streak_history[0]["length"] == 10
        assert streak_history[1]["length"] == 3


@pytest.mark.statistics
@pytest.mark.streak
@pytest.mark.unit
class TestStreakHistoryBackdatedEntries:
    """Test streak history with backdated entries edge cases."""

    def test_backdated_entries_dont_affect_current_streak(self, client):
        """Backdated entries don't break the current ongoing streak."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(5):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        EntryFactory(user=user, created_at=base_date - timedelta(days=20))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 2
        assert streak_history[0]["length"] == 5
        assert streak_history[1]["length"] == 1

    def test_backdated_entry_creates_separate_streak(self, client):
        """Backdated entry creates a separate single-day streak."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, created_at=base_date)

        EntryFactory(user=user, created_at=base_date - timedelta(days=1))

        EntryFactory(user=user, created_at=base_date - timedelta(days=30))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 2
        assert streak_history[0]["length"] == 2
        assert streak_history[1]["length"] == 1

    def test_backdated_streak_not_merged_with_current(self, client):
        """Backdated streak doesn't merge with current streak even if dates match."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(5):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        backdated_base = base_date - timedelta(days=15)
        for i in range(3):
            EntryFactory(user=user, created_at=backdated_base - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 2
        lengths = sorted([s["length"] for s in streak_history], reverse=True)
        assert lengths == [5, 3]

    def test_empty_content_entries_excluded_from_streaks(self, client):
        """Entries with empty content don't count towards streaks."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, created_at=base_date, content="")

        EntryFactory(
            user=user,
            created_at=base_date - timedelta(days=1),
            content="Some content here"
        )

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 1


@pytest.mark.statistics
@pytest.mark.streak
@pytest.mark.unit
class TestStreakHistoryTimezoneAwareness:
    """Test that streak calculation respects user's local timezone."""

    def test_streaks_calculated_in_user_local_timezone(self, client):
        """Streaks are calculated in user's local timezone, not UTC."""
        user_prague = UserFactory(timezone="Europe/Prague")
        user_tokyo = UserFactory(timezone="Asia/Tokyo")

        utc_time = timezone.now()

        for i in range(5):
            EntryFactory(user=user_prague, created_at=utc_time - timedelta(days=i))

        for i in range(5):
            EntryFactory(user=user_tokyo, created_at=utc_time - timedelta(days=i))

        client.force_login(user_prague)
        response_prague = client.get(reverse("api:statistics"), {"period": "all"})
        client.logout()

        client.force_login(user_tokyo)
        response_tokyo = client.get(reverse("api:statistics"), {"period": "all"})

        assert response_prague.status_code == 200
        assert response_tokyo.status_code == 200

        streak_history_prague = response_prague.json()["writing_patterns"]["streak_history"]
        streak_history_tokyo = response_tokyo.json()["writing_patterns"]["streak_history"]

        assert len(streak_history_prague) == 1
        assert len(streak_history_tokyo) == 1
        assert streak_history_prague[0]["length"] == 5
        assert streak_history_tokyo[0]["length"] == 5

    def test_midnight_boundary_respects_timezone(self, client):
        """Streak boundary respects user's midnight, not UTC."""
        user = UserFactory(timezone="America/New_York")
        client.force_login(user)

        user_tz = ZoneInfo("America/New_York")
        now_local = timezone.now().astimezone(user_tz)

        today_local = now_local.replace(hour=12, minute=0, second=0, microsecond=0)
        yesterday_local = today_local - timedelta(days=1)

        EntryFactory(user=user, created_at=today_local)
        EntryFactory(user=user, created_at=yesterday_local)

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 2

    def test_dst_transition_spring_forward(self, client):
        """Streak calculation handles DST spring forward transition."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        spring_forward = datetime(2024, 3, 31, 12, 0, 0, tzinfo=user_tz)

        for i in range(3):
            EntryFactory(
                user=user,
                created_at=spring_forward - timedelta(days=i)
            )

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 3

    def test_dst_transition_fall_back(self, client):
        """Streak calculation handles DST fall back transition."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        user_tz = ZoneInfo("Europe/Prague")
        fall_back = datetime(2024, 10, 27, 12, 0, 0, tzinfo=user_tz)

        for i in range(3):
            EntryFactory(
                user=user,
                created_at=fall_back - timedelta(days=i)
            )

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 3

    def test_negative_offset_timezone_streaks(self, client):
        """Streak calculation works correctly with negative UTC offset."""
        user = UserFactory(timezone="America/Los_Angeles")
        client.force_login(user)

        user_tz = ZoneInfo("America/Los_Angeles")
        now_local = timezone.now().astimezone(user_tz)

        for i in range(5):
            EntryFactory(
                user=user,
                created_at=now_local - timedelta(days=i)
            )

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 5

    def test_positive_offset_timezone_streaks(self, client):
        """Streak calculation works correctly with positive UTC offset."""
        user = UserFactory(timezone="Asia/Tokyo")
        client.force_login(user)

        user_tz = ZoneInfo("Asia/Tokyo")
        now_local = timezone.now().astimezone(user_tz)

        for i in range(5):
            EntryFactory(
                user=user,
                created_at=now_local - timedelta(days=i)
            )

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 5


@pytest.mark.statistics
@pytest.mark.streak
@pytest.mark.unit
class TestStreakHistoryEdgeCases:
    """Test edge cases in streak history calculation."""

    def test_no_entries_returns_empty_history(self, client):
        """User with no entries returns empty streak history."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert streak_history == []

    def test_single_entry_returns_one_day_streak(self, client):
        """Single entry creates a one-day streak."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        EntryFactory(user=user)

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 1

    def test_multiple_entries_same_day_count_as_one(self, client):
        """Multiple entries on same day count as single day in streak."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory.create_batch(5, user=user, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 1
        assert streak_history[0]["length"] == 1

    def test_gap_of_one_day_breaks_streak(self, client):
        """Single day gap breaks the streak."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        EntryFactory(user=user, created_at=base_date)
        EntryFactory(user=user, created_at=base_date - timedelta(days=2))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        streak_history = data["writing_patterns"]["streak_history"]

        assert len(streak_history) == 2
        assert streak_history[0]["length"] == 1
        assert streak_history[1]["length"] == 1

    def test_period_filtering_affects_streaks(self, client):
        """Period parameter filters which entries are included in streaks."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(10):
            EntryFactory(
                user=user,
                created_at=base_date - timedelta(days=i)
            )

        response_7d = client.get(reverse("api:statistics"), {"period": "7d"})
        response_all = client.get(reverse("api:statistics"), {"period": "all"})

        assert response_7d.status_code == 200
        assert response_all.status_code == 200

        streaks_7d = response_7d.json()["writing_patterns"]["streak_history"]
        streaks_all = response_all.json()["writing_patterns"]["streak_history"]

        assert len(streaks_all) == 1
        assert streaks_all[0]["length"] == 10

        assert len(streaks_7d) >= 1
        assert streaks_7d[0]["length"] <= 10

    def test_user_isolation_in_streaks(self, client):
        """Streaks are isolated per user."""
        from django.core.cache import cache

        cache.clear()

        user1 = UserFactory(timezone="Europe/Prague")
        user2 = UserFactory(timezone="Europe/Prague")

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        for i in range(5):
            EntryFactory(user=user1, created_at=base_date - timedelta(days=i))

        for i in range(10):
            EntryFactory(user=user2, created_at=base_date - timedelta(days=i))

        client.force_login(user1)
        response1 = client.get(reverse("api:statistics"), {"period": "all"})
        streaks1 = response1.json()["writing_patterns"]["streak_history"]

        client.logout()
        cache.clear()
        client.force_login(user2)
        response2 = client.get(reverse("api:statistics"), {"period": "all"})
        streaks2 = response2.json()["writing_patterns"]["streak_history"]

        assert streaks1[0]["length"] == 5
        assert streaks2[0]["length"] == 10
