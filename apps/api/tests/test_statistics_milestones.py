"""
Comprehensive tests for milestones calculation in statistics API.

Tests cover:
- User with no entries (all milestones unachieved)
- Entry milestones (1, 10, 50, 100, 365, 500, 1000)
- Word count milestones (1000, 10000, 50000, 100000, 250000, 500000, 1000000)
- Streak milestones based on User.longest_streak (7, 30, 100, 365)
- Correct structure of response
- Period independence (milestones calculated from ALL user data)
- User isolation
"""

import pytest
from datetime import timedelta
from zoneinfo import ZoneInfo
from django.urls import reverse
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory


@pytest.mark.statistics
@pytest.mark.unit
class TestMilestonesResponseStructure:
    """Test the structure of milestones response."""

    def test_milestones_key_exists_in_response(self, client):
        """Response contains milestones key."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        assert "milestones" in data

    def test_milestones_contains_list(self, client):
        """Milestones response contains a list of milestones."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        assert "milestones" in data["milestones"]
        assert isinstance(data["milestones"]["milestones"], list)

    def test_milestone_item_structure(self, client):
        """Each milestone item has required fields: type, value, achieved, current."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        assert len(milestones) > 0
        for milestone in milestones:
            assert "type" in milestone
            assert "value" in milestone
            assert "achieved" in milestone
            assert "current" in milestone
            assert milestone["type"] in ["entries", "words", "streak"]
            assert isinstance(milestone["value"], int)
            assert isinstance(milestone["achieved"], bool)
            assert isinstance(milestone["current"], int)

    def test_correct_number_of_milestones(self, client):
        """Response contains correct number of milestones (7 entry + 7 word + 4 streak = 18)."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        # 7 entry milestones + 7 word milestones + 4 streak milestones = 18
        assert len(milestones) == 18

    def test_entry_milestones_thresholds(self, client):
        """Entry milestones have correct threshold values."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        entry_milestones = [m for m in milestones if m["type"] == "entries"]
        entry_values = sorted([m["value"] for m in entry_milestones])

        assert entry_values == [1, 10, 50, 100, 365, 500, 1000]

    def test_word_milestones_thresholds(self, client):
        """Word milestones have correct threshold values."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        word_milestones = [m for m in milestones if m["type"] == "words"]
        word_values = sorted([m["value"] for m in word_milestones])

        assert word_values == [1000, 10000, 50000, 100000, 250000, 500000, 1000000]

    def test_streak_milestones_thresholds(self, client):
        """Streak milestones have correct threshold values."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        streak_milestones = [m for m in milestones if m["type"] == "streak"]
        streak_values = sorted([m["value"] for m in streak_milestones])

        assert streak_values == [7, 30, 100, 365]


@pytest.mark.statistics
@pytest.mark.unit
class TestMilestonesNoEntries:
    """Test milestones for user with no entries."""

    def test_no_entries_all_milestones_unachieved(self, client):
        """User with no entries has all milestones unachieved."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        for milestone in milestones:
            assert milestone["achieved"] is False

    def test_no_entries_current_values_zero(self, client):
        """User with no entries has current values of zero."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        entry_milestones = [m for m in milestones if m["type"] == "entries"]
        word_milestones = [m for m in milestones if m["type"] == "words"]
        streak_milestones = [m for m in milestones if m["type"] == "streak"]

        for milestone in entry_milestones:
            assert milestone["current"] == 0

        for milestone in word_milestones:
            assert milestone["current"] == 0

        for milestone in streak_milestones:
            assert milestone["current"] == 0


@pytest.mark.statistics
@pytest.mark.unit
class TestEntryMilestones:
    """Test entry count milestones calculation."""

    def test_first_entry_milestone_achieved(self, client):
        """First entry milestone is achieved with 1 entry."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        EntryFactory(user=user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        entry_milestones = [m for m in milestones if m["type"] == "entries"]
        first_entry_milestone = next(m for m in entry_milestones if m["value"] == 1)

        assert first_entry_milestone["achieved"] is True
        assert first_entry_milestone["current"] == 1

    def test_ten_entries_milestone_achieved(self, client):
        """Ten entries milestone is achieved with 10 entries."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        for i in range(10):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        entry_milestones = [m for m in milestones if m["type"] == "entries"]
        ten_entry_milestone = next(m for m in entry_milestones if m["value"] == 10)

        assert ten_entry_milestone["achieved"] is True
        assert ten_entry_milestone["current"] == 10

    def test_entry_milestone_not_achieved_below_threshold(self, client):
        """Entry milestone not achieved when below threshold."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        for i in range(9):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        entry_milestones = [m for m in milestones if m["type"] == "entries"]
        ten_entry_milestone = next(m for m in entry_milestones if m["value"] == 10)

        assert ten_entry_milestone["achieved"] is False
        assert ten_entry_milestone["current"] == 9

    def test_entry_current_value_accurate(self, client):
        """Entry milestone current value is accurate."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        for i in range(127):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        entry_milestones = [m for m in milestones if m["type"] == "entries"]

        for milestone in entry_milestones:
            assert milestone["current"] == 127

        # Check which milestones are achieved
        achieved_milestones = [m for m in entry_milestones if m["achieved"]]
        achieved_values = [m["value"] for m in achieved_milestones]
        assert 1 in achieved_values
        assert 10 in achieved_values
        assert 50 in achieved_values
        assert 100 in achieved_values
        assert 365 not in achieved_values  # 127 < 365

    def test_multiple_entries_same_day_count_separately(self, client):
        """Multiple entries on same day each count towards entry milestones."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        # Create 5 entries on same day
        for _ in range(5):
            EntryFactory(user=user, created_at=base_date)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        entry_milestones = [m for m in milestones if m["type"] == "entries"]
        first_entry_milestone = next(m for m in entry_milestones if m["value"] == 1)

        assert first_entry_milestone["current"] == 5
        assert first_entry_milestone["achieved"] is True


@pytest.mark.statistics
@pytest.mark.unit
class TestWordMilestones:
    """Test word count milestones calculation."""

    def test_word_milestone_current_value_calculation(self, client):
        """Word milestone current value is sum of all entry word counts."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        # Create entries with known word counts
        entry1 = EntryFactory(user=user, content="word " * 500, created_at=base_date)
        entry1.refresh_from_db()
        entry2 = EntryFactory(
            user=user, content="word " * 600, created_at=base_date - timedelta(days=1)
        )
        entry2.refresh_from_db()

        expected_total = entry1.word_count + entry2.word_count

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        word_milestones = [m for m in milestones if m["type"] == "words"]

        for milestone in word_milestones:
            assert milestone["current"] == expected_total

    def test_first_word_milestone_achieved(self, client):
        """1000 word milestone is achieved with 1000+ words."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        # Create entry with 1000+ words
        EntryFactory(user=user, content="word " * 1100)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        word_milestones = [m for m in milestones if m["type"] == "words"]
        first_word_milestone = next(m for m in word_milestones if m["value"] == 1000)

        assert first_word_milestone["achieved"] is True
        assert first_word_milestone["current"] >= 1000

    def test_word_milestone_not_achieved_below_threshold(self, client):
        """Word milestone not achieved when below threshold."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        # Create entry with less than 1000 words
        EntryFactory(user=user, content="word " * 500)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        word_milestones = [m for m in milestones if m["type"] == "words"]
        first_word_milestone = next(m for m in word_milestones if m["value"] == 1000)

        assert first_word_milestone["achieved"] is False
        assert first_word_milestone["current"] < 1000

    def test_large_word_count_milestones(self, client):
        """Large word count milestones are correctly calculated."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))
        # Create 100 entries with 1000 words each = 100,000 words
        for i in range(100):
            EntryFactory(
                user=user,
                content="word " * 1000,
                created_at=base_date - timedelta(days=i),
            )

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        word_milestones = [m for m in milestones if m["type"] == "words"]

        # Should have achieved 1000, 10000, 50000, 100000 milestones
        achieved_milestones = [m for m in word_milestones if m["achieved"]]
        achieved_values = [m["value"] for m in achieved_milestones]

        assert 1000 in achieved_values
        assert 10000 in achieved_values
        assert 50000 in achieved_values
        assert 100000 in achieved_values
        # Not achieved yet
        assert 250000 not in achieved_values
        assert 500000 not in achieved_values
        assert 1000000 not in achieved_values

    def test_empty_entries_dont_add_words(self, client):
        """Empty entries (word_count=0) don't add to word milestones."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        # Create empty entry
        EntryFactory(user=user, content="")

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        word_milestones = [m for m in milestones if m["type"] == "words"]
        first_word_milestone = next(m for m in word_milestones if m["value"] == 1000)

        assert first_word_milestone["current"] == 0
        assert first_word_milestone["achieved"] is False


@pytest.mark.statistics
@pytest.mark.streak
@pytest.mark.unit
class TestStreakMilestones:
    """Test streak milestones based on User.longest_streak."""

    def test_streak_milestones_use_longest_streak(self, client):
        """Streak milestones use longest_streak from User model."""
        user = UserFactory(timezone="Europe/Prague", longest_streak=15)
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        streak_milestones = [m for m in milestones if m["type"] == "streak"]

        for milestone in streak_milestones:
            assert milestone["current"] == 15

    def test_seven_day_streak_milestone_achieved(self, client):
        """7-day streak milestone is achieved with longest_streak >= 7."""
        user = UserFactory(timezone="Europe/Prague", longest_streak=7)
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        streak_milestones = [m for m in milestones if m["type"] == "streak"]
        seven_day_milestone = next(m for m in streak_milestones if m["value"] == 7)

        assert seven_day_milestone["achieved"] is True
        assert seven_day_milestone["current"] == 7

    def test_streak_milestone_not_achieved_below_threshold(self, client):
        """Streak milestone not achieved when longest_streak below threshold."""
        user = UserFactory(timezone="Europe/Prague", longest_streak=6)
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        streak_milestones = [m for m in milestones if m["type"] == "streak"]
        seven_day_milestone = next(m for m in streak_milestones if m["value"] == 7)

        assert seven_day_milestone["achieved"] is False
        assert seven_day_milestone["current"] == 6

    def test_thirty_day_streak_milestone(self, client):
        """30-day streak milestone is correctly evaluated."""
        user = UserFactory(timezone="Europe/Prague", longest_streak=30)
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        streak_milestones = [m for m in milestones if m["type"] == "streak"]
        thirty_day_milestone = next(m for m in streak_milestones if m["value"] == 30)

        assert thirty_day_milestone["achieved"] is True
        assert thirty_day_milestone["current"] == 30

    def test_hundred_day_streak_milestone(self, client):
        """100-day streak milestone is correctly evaluated."""
        user = UserFactory(timezone="Europe/Prague", longest_streak=100)
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        streak_milestones = [m for m in milestones if m["type"] == "streak"]
        hundred_day_milestone = next(m for m in streak_milestones if m["value"] == 100)

        assert hundred_day_milestone["achieved"] is True
        assert hundred_day_milestone["current"] == 100

    def test_year_streak_milestone(self, client):
        """365-day streak milestone is correctly evaluated."""
        user = UserFactory(timezone="Europe/Prague", longest_streak=365)
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        streak_milestones = [m for m in milestones if m["type"] == "streak"]
        year_milestone = next(m for m in streak_milestones if m["value"] == 365)

        assert year_milestone["achieved"] is True
        assert year_milestone["current"] == 365

    def test_streak_milestones_with_exceeding_value(self, client):
        """Streak milestones correctly show achieved when value exceeds threshold."""
        user = UserFactory(timezone="Europe/Prague", longest_streak=50)
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        streak_milestones = [m for m in milestones if m["type"] == "streak"]

        # 7 and 30 should be achieved
        seven_day = next(m for m in streak_milestones if m["value"] == 7)
        thirty_day = next(m for m in streak_milestones if m["value"] == 30)
        hundred_day = next(m for m in streak_milestones if m["value"] == 100)
        year = next(m for m in streak_milestones if m["value"] == 365)

        assert seven_day["achieved"] is True
        assert thirty_day["achieved"] is True
        assert hundred_day["achieved"] is False
        assert year["achieved"] is False

        # All should show current = 50
        for milestone in streak_milestones:
            assert milestone["current"] == 50

    def test_zero_streak_no_milestones_achieved(self, client):
        """User with zero longest_streak has no streak milestones achieved."""
        user = UserFactory(timezone="Europe/Prague", longest_streak=0)
        client.force_login(user)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        streak_milestones = [m for m in milestones if m["type"] == "streak"]

        for milestone in streak_milestones:
            assert milestone["achieved"] is False
            assert milestone["current"] == 0


@pytest.mark.statistics
@pytest.mark.unit
class TestMilestonesPeriodIndependence:
    """Test that milestones are calculated from ALL user data, not period-filtered."""

    def test_milestones_include_entries_outside_period(self, client):
        """Milestones include entries outside the requested period."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        # Create 5 entries in last 7 days
        for i in range(5):
            EntryFactory(user=user, created_at=base_date - timedelta(days=i))

        # Create 10 entries outside 7-day period (20+ days ago)
        for i in range(10):
            EntryFactory(user=user, created_at=base_date - timedelta(days=20 + i))

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        entry_milestones = [m for m in milestones if m["type"] == "entries"]
        first_entry = next(m for m in entry_milestones if m["value"] == 1)
        ten_entry = next(m for m in entry_milestones if m["value"] == 10)

        # Should include all 15 entries, not just the 5 from last 7 days
        assert first_entry["current"] == 15
        assert ten_entry["current"] == 15
        assert ten_entry["achieved"] is True

    def test_milestones_same_across_different_periods(self, client):
        """Milestones are identical regardless of period parameter."""
        user = UserFactory(timezone="Europe/Prague", longest_streak=10)
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        # Create entries across different time ranges
        for i in range(20):
            EntryFactory(
                user=user,
                content="word " * 100,
                created_at=base_date - timedelta(days=i * 10),
            )

        response_7d = client.get(reverse("api:statistics"), {"period": "7d"})
        response_30d = client.get(reverse("api:statistics"), {"period": "30d"})
        response_all = client.get(reverse("api:statistics"), {"period": "all"})

        assert response_7d.status_code == 200
        assert response_30d.status_code == 200
        assert response_all.status_code == 200

        milestones_7d = response_7d.json()["milestones"]["milestones"]
        milestones_30d = response_30d.json()["milestones"]["milestones"]
        milestones_all = response_all.json()["milestones"]["milestones"]

        # All milestones should be identical
        for i, milestone in enumerate(milestones_7d):
            assert milestone["current"] == milestones_30d[i]["current"]
            assert milestone["current"] == milestones_all[i]["current"]
            assert milestone["achieved"] == milestones_30d[i]["achieved"]
            assert milestone["achieved"] == milestones_all[i]["achieved"]

    def test_word_milestones_include_old_entries(self, client):
        """Word milestones include words from entries outside current period."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        # Create entry with 500 words in last 7 days
        entry_recent = EntryFactory(
            user=user, content="word " * 500, created_at=base_date
        )
        entry_recent.refresh_from_db()

        # Create entry with 600 words outside 7-day period
        entry_old = EntryFactory(
            user=user, content="word " * 600, created_at=base_date - timedelta(days=30)
        )
        entry_old.refresh_from_db()

        expected_total = entry_recent.word_count + entry_old.word_count

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        word_milestones = [m for m in milestones if m["type"] == "words"]
        first_word = next(m for m in word_milestones if m["value"] == 1000)

        assert first_word["current"] == expected_total
        assert first_word["achieved"] is True  # > 1000 words


@pytest.mark.statistics
@pytest.mark.unit
class TestMilestonesUserIsolation:
    """Test that milestones are isolated per user."""

    def test_milestones_only_include_current_user_entries(self, client):
        """Milestones only count current user's entries."""
        from django.core.cache import cache

        cache.clear()

        user1 = UserFactory(timezone="Europe/Prague")
        user2 = UserFactory(timezone="Europe/Prague")

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        # Create 5 entries for user1
        for i in range(5):
            EntryFactory(user=user1, created_at=base_date - timedelta(days=i))

        # Create 15 entries for user2
        for i in range(15):
            EntryFactory(user=user2, created_at=base_date - timedelta(days=i))

        client.force_login(user1)
        response1 = client.get(reverse("api:statistics"), {"period": "all"})

        client.logout()
        cache.clear()

        client.force_login(user2)
        response2 = client.get(reverse("api:statistics"), {"period": "all"})

        assert response1.status_code == 200
        assert response2.status_code == 200

        milestones1 = response1.json()["milestones"]["milestones"]
        milestones2 = response2.json()["milestones"]["milestones"]

        entry_milestones1 = [m for m in milestones1 if m["type"] == "entries"]
        entry_milestones2 = [m for m in milestones2 if m["type"] == "entries"]

        # User1 should have 5 entries
        assert entry_milestones1[0]["current"] == 5
        # User2 should have 15 entries
        assert entry_milestones2[0]["current"] == 15

    def test_streak_milestones_use_current_user_streak(self, client):
        """Streak milestones use current user's longest_streak."""
        from django.core.cache import cache

        cache.clear()

        user1 = UserFactory(timezone="Europe/Prague", longest_streak=10)
        user2 = UserFactory(timezone="Europe/Prague", longest_streak=50)

        client.force_login(user1)
        response1 = client.get(reverse("api:statistics"), {"period": "7d"})

        client.logout()
        cache.clear()

        client.force_login(user2)
        response2 = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response1.status_code == 200
        assert response2.status_code == 200

        milestones1 = response1.json()["milestones"]["milestones"]
        milestones2 = response2.json()["milestones"]["milestones"]

        streak_milestones1 = [m for m in milestones1 if m["type"] == "streak"]
        streak_milestones2 = [m for m in milestones2 if m["type"] == "streak"]

        # User1 should have streak of 10
        for milestone in streak_milestones1:
            assert milestone["current"] == 10

        # User2 should have streak of 50
        for milestone in streak_milestones2:
            assert milestone["current"] == 50


@pytest.mark.statistics
@pytest.mark.integration
class TestMilestonesIntegration:
    """Integration tests for milestones endpoint."""

    def test_milestones_requires_authentication(self, client):
        """Unauthenticated users cannot access milestones."""
        response = client.get(reverse("api:statistics"))

        assert response.status_code == 403

    def test_milestones_with_all_milestone_types_achieved(self, client):
        """User with significant activity has multiple milestones achieved."""
        from django.core.cache import cache
        from django.contrib.auth import get_user_model

        User = get_user_model()
        cache.clear()

        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        base_date = timezone.now().astimezone(ZoneInfo("Europe/Prague"))

        # Create 55 CONSECUTIVE entries with 200 words each = 11,000 words total
        # This will create a 55-day streak starting from today backwards
        for i in range(55):
            EntryFactory(
                user=user,
                content="word " * 200,
                created_at=base_date - timedelta(days=i),
            )

        # Manually set longest_streak AFTER entries are created (signals have run)
        # to simulate a user who had a longer streak in the past
        User.objects.filter(pk=user.pk).update(longest_streak=55)
        user.refresh_from_db()

        # Clear cache to ensure fresh API response
        cache.clear()

        response = client.get(reverse("api:statistics"), {"period": "all"})

        assert response.status_code == 200
        data = response.json()
        milestones = data["milestones"]["milestones"]

        # Entry milestones: 1, 10, 50 should be achieved
        entry_milestones = [m for m in milestones if m["type"] == "entries"]
        achieved_entry = [m["value"] for m in entry_milestones if m["achieved"]]
        assert 1 in achieved_entry
        assert 10 in achieved_entry
        assert 50 in achieved_entry
        assert 100 not in achieved_entry

        # Word milestones: 1000, 10000 should be achieved
        word_milestones = [m for m in milestones if m["type"] == "words"]
        achieved_word = [m["value"] for m in word_milestones if m["achieved"]]
        assert 1000 in achieved_word
        assert 10000 in achieved_word
        assert 50000 not in achieved_word

        # Streak milestones: 7, 30 should be achieved (55-day longest streak)
        streak_milestones = [m for m in milestones if m["type"] == "streak"]
        achieved_streak = [m["value"] for m in streak_milestones if m["achieved"]]
        assert 7 in achieved_streak
        assert 30 in achieved_streak
        assert 100 not in achieved_streak

    def test_milestones_response_is_json_serializable(self, client):
        """Milestones response is properly JSON serializable."""
        import json

        user = UserFactory(timezone="Europe/Prague", longest_streak=10)
        client.force_login(user)

        EntryFactory(user=user, content="word " * 500)

        response = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response.status_code == 200

        # Should not raise any exception
        parsed = json.loads(response.content)
        assert "milestones" in parsed
        assert "milestones" in parsed["milestones"]

    def test_milestones_caching_behavior(self, client):
        """Milestones are included in cached response."""
        user = UserFactory(timezone="Europe/Prague")
        client.force_login(user)

        EntryFactory(user=user)

        response1 = client.get(reverse("api:statistics"), {"period": "7d"})
        response2 = client.get(reverse("api:statistics"), {"period": "7d"})

        assert response1.status_code == 200
        assert response2.status_code == 200

        milestones1 = response1.json()["milestones"]
        milestones2 = response2.json()["milestones"]

        assert milestones1 == milestones2
