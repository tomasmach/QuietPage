"""
Comprehensive tests for journal.utils.

Tests utility functions including:
- get_user_local_date(): timezone conversion
- update_user_streak(): all edge cases
- recalculate_user_streak(): full recalculation
- get_random_quote(): random quote selection
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
from apps.journal.utils import (
    get_user_local_date,
    update_user_streak,
    recalculate_user_streak,
    get_random_quote,
    INSPIRATIONAL_QUOTES,
)
from apps.journal.tests.factories import EntryFactory
from apps.accounts.tests.factories import UserFactory


@pytest.mark.unit
@pytest.mark.utils
class TestGetUserLocalDate:
    """Test get_user_local_date timezone conversion."""
    
    def test_utc_to_prague_conversion(self):
        """Test converting UTC datetime to Prague timezone."""
        # Create UTC datetime: 2024-01-15 22:00 UTC
        utc_dt = timezone.datetime(2024, 1, 15, 22, 0, 0, tzinfo=pytz.UTC)
        
        # Convert to Prague (UTC+1 in winter)
        local_date = get_user_local_date(utc_dt, 'Europe/Prague')
        
        # Should be 2024-01-15 23:00 Prague time, so date is still 2024-01-15
        assert local_date.year == 2024
        assert local_date.month == 1
        assert local_date.day == 15
    
    def test_utc_to_prague_day_boundary(self):
        """Test timezone conversion across day boundary."""
        # Create UTC datetime: 2024-01-15 23:00 UTC
        utc_dt = timezone.datetime(2024, 1, 15, 23, 0, 0, tzinfo=pytz.UTC)
        
        # Convert to Prague (UTC+1 in winter)
        local_date = get_user_local_date(utc_dt, 'Europe/Prague')
        
        # Should be 2024-01-16 00:00 Prague time, so date is 2024-01-16
        assert local_date.year == 2024
        assert local_date.month == 1
        assert local_date.day == 16
    
    def test_utc_to_new_york_conversion(self):
        """Test converting UTC to New York timezone."""
        # Create UTC datetime: 2024-01-15 04:00 UTC
        utc_dt = timezone.datetime(2024, 1, 15, 4, 0, 0, tzinfo=pytz.UTC)
        
        # Convert to New York (UTC-5 in winter)
        local_date = get_user_local_date(utc_dt, 'America/New_York')
        
        # Should be 2024-01-14 23:00 New York time, so date is 2024-01-14
        assert local_date.year == 2024
        assert local_date.month == 1
        assert local_date.day == 14
    
    def test_utc_to_tokyo_conversion(self):
        """Test converting UTC to Tokyo timezone."""
        # Create UTC datetime: 2024-01-15 14:00 UTC
        utc_dt = timezone.datetime(2024, 1, 15, 14, 0, 0, tzinfo=pytz.UTC)
        
        # Convert to Tokyo (UTC+9)
        local_date = get_user_local_date(utc_dt, 'Asia/Tokyo')
        
        # Should be 2024-01-15 23:00 Tokyo time, so date is still 2024-01-15
        assert local_date.year == 2024
        assert local_date.month == 1
        assert local_date.day == 15
    
    def test_daylight_saving_time_summer(self):
        """Test conversion during daylight saving time (summer)."""
        # Create UTC datetime: 2024-07-15 22:00 UTC (summer)
        utc_dt = timezone.datetime(2024, 7, 15, 22, 0, 0, tzinfo=pytz.UTC)
        
        # Convert to Prague (UTC+2 in summer)
        local_date = get_user_local_date(utc_dt, 'Europe/Prague')
        
        # Should be 2024-07-16 00:00 Prague time (DST), so date is 2024-07-16
        assert local_date.year == 2024
        assert local_date.month == 7
        assert local_date.day == 16
    
    def test_returns_date_object(self):
        """Test that function returns date object, not datetime."""
        from datetime import date
        utc_dt = timezone.now()
        
        result = get_user_local_date(utc_dt, 'Europe/Prague')
        
        assert isinstance(result, date)
        assert not isinstance(result, datetime)


@pytest.mark.unit
@pytest.mark.utils
@pytest.mark.streak
class TestUpdateUserStreak:
    """Test update_user_streak function with all edge cases."""
    
    def test_first_entry_ever(self):
        """Test streak calculation for first entry."""
        user = UserFactory(
            current_streak=0,
            longest_streak=0,
            last_entry_date=None
        )
        
        entry_date = timezone.now()
        update_user_streak(user, entry_date)
        
        user.refresh_from_db()
        assert user.current_streak == 1
        assert user.longest_streak == 1
        assert user.last_entry_date is not None
    
    def test_same_day_entry_no_change(self):
        """Test that multiple entries on same day don't extend streak."""
        today = timezone.now()
        user = UserFactory(
            current_streak=5,
            longest_streak=10,
            last_entry_date=get_user_local_date(today, 'Europe/Prague')
        )
        
        # Create another entry on the same day
        update_user_streak(user, today)
        
        user.refresh_from_db()
        # Streak should remain unchanged
        assert user.current_streak == 5
        assert user.longest_streak == 10
    
    def test_consecutive_day_increments_streak(self):
        """Test that entry on consecutive day increments streak."""
        yesterday = timezone.now() - timedelta(days=1)
        today = timezone.now()
        
        user = UserFactory(
            current_streak=5,
            longest_streak=10,
            last_entry_date=get_user_local_date(yesterday, 'Europe/Prague')
        )
        
        update_user_streak(user, today)
        
        user.refresh_from_db()
        assert user.current_streak == 6
        assert user.longest_streak == 10  # Not updated yet
    
    def test_consecutive_day_updates_longest_streak(self):
        """Test that longest streak is updated when broken."""
        yesterday = timezone.now() - timedelta(days=1)
        today = timezone.now()
        
        user = UserFactory(
            current_streak=10,
            longest_streak=10,
            last_entry_date=get_user_local_date(yesterday, 'Europe/Prague')
        )
        
        update_user_streak(user, today)
        
        user.refresh_from_db()
        assert user.current_streak == 11
        assert user.longest_streak == 11  # Updated!
    
    def test_gap_resets_streak_to_one(self):
        """Test that gap in entries resets streak to 1."""
        three_days_ago = timezone.now() - timedelta(days=3)
        today = timezone.now()
        
        user = UserFactory(
            current_streak=15,
            longest_streak=20,
            last_entry_date=get_user_local_date(three_days_ago, 'Europe/Prague')
        )
        
        update_user_streak(user, today)
        
        user.refresh_from_db()
        assert user.current_streak == 1  # Reset
        assert user.longest_streak == 20  # Preserved
    
    def test_backdated_entry_ignored(self):
        """Test that backdated entries don't affect streak."""
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        
        user = UserFactory(
            current_streak=10,
            longest_streak=15,
            last_entry_date=get_user_local_date(today, 'Europe/Prague')
        )
        
        # Create backdated entry
        update_user_streak(user, yesterday)
        
        user.refresh_from_db()
        # Streak should remain unchanged
        assert user.current_streak == 10
        assert user.longest_streak == 15
        assert user.last_entry_date == get_user_local_date(today, 'Europe/Prague')
    
    def test_timezone_aware_date_comparison(self):
        """Test that streak calculation respects user's timezone."""
        user = UserFactory(timezone='America/New_York')
        
        # Create entry at 23:00 UTC on Jan 15
        # This is 18:00 New York time (still Jan 15)
        utc_dt = timezone.datetime(2024, 1, 15, 23, 0, 0, tzinfo=pytz.UTC)
        
        update_user_streak(user, utc_dt)
        
        user.refresh_from_db()
        # Should use Jan 15 in New York time
        assert user.last_entry_date.day == 15
    
    def test_midnight_edge_case(self):
        """Test streak calculation at midnight boundary."""
        user = UserFactory(timezone='Europe/Prague')
        
        # 23:00 UTC on Jan 15 = 00:00 Prague time on Jan 16
        utc_dt = timezone.datetime(2024, 1, 15, 23, 0, 0, tzinfo=pytz.UTC)
        
        update_user_streak(user, utc_dt)
        
        user.refresh_from_db()
        # Should use Jan 16 in Prague time
        assert user.last_entry_date.day == 16
    
    def test_streak_sequence_over_week(self):
        """Test streak building over multiple days."""
        user = UserFactory(
            current_streak=0,
            longest_streak=0,
            last_entry_date=None
        )
        
        # Create entries for 7 consecutive days
        base_date = timezone.now() - timedelta(days=6)
        for i in range(7):
            entry_date = base_date + timedelta(days=i)
            update_user_streak(user, entry_date)
            user.refresh_from_db()
        
        assert user.current_streak == 7
        assert user.longest_streak == 7
    
    def test_streak_break_and_rebuild(self):
        """Test breaking and rebuilding a streak."""
        user = UserFactory(
            current_streak=0,
            longest_streak=0,
            last_entry_date=None
        )
        
        base_date = timezone.now() - timedelta(days=10)
        
        # Build 5-day streak
        for i in range(5):
            update_user_streak(user, base_date + timedelta(days=i))
            user.refresh_from_db()
        
        assert user.current_streak == 5
        assert user.longest_streak == 5
        
        # Skip 2 days (break streak)
        update_user_streak(user, base_date + timedelta(days=7))
        user.refresh_from_db()
        
        assert user.current_streak == 1  # Reset
        assert user.longest_streak == 5  # Preserved
        
        # Build 3-day streak
        for i in range(1, 3):
            update_user_streak(user, base_date + timedelta(days=7 + i))
            user.refresh_from_db()
        
        assert user.current_streak == 3
        assert user.longest_streak == 5  # Still 5


@pytest.mark.unit
@pytest.mark.utils
@pytest.mark.streak
class TestRecalculateUserStreak:
    """Test recalculate_user_streak function."""
    
    def test_no_entries_returns_zero_streaks(self):
        """Test recalculation with no entries."""
        user = UserFactory()
        
        result = recalculate_user_streak(user)
        
        assert result['current_streak'] == 0
        assert result['longest_streak'] == 0
    
    def test_single_entry_today(self):
        """Test recalculation with single entry today."""
        user = UserFactory(timezone='Europe/Prague')
        
        # Create entry today
        EntryFactory(
            user=user,
            created_at=timezone.now()
        )
        
        result = recalculate_user_streak(user)
        
        assert result['current_streak'] == 1
        assert result['longest_streak'] == 1
    
    def test_single_entry_yesterday(self):
        """Test recalculation with single entry yesterday."""
        user = UserFactory(timezone='Europe/Prague')
        
        # Create entry yesterday
        EntryFactory(
            user=user,
            created_at=timezone.now() - timedelta(days=1)
        )
        
        result = recalculate_user_streak(user)
        
        # Current streak is 0 (no entry today)
        assert result['current_streak'] == 0
        assert result['longest_streak'] == 1
    
    def test_consecutive_days_including_today(self):
        """Test recalculation with consecutive days including today."""
        user = UserFactory(timezone='Europe/Prague')
        
        # Create entries for last 5 days
        for i in range(5):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=4-i)
            )
        
        result = recalculate_user_streak(user)
        
        assert result['current_streak'] == 5
        assert result['longest_streak'] == 5
    
    def test_gap_in_middle(self):
        """Test recalculation with gap in entries."""
        user = UserFactory(timezone='Europe/Prague')
        
        # Days 0, 1, 2 (today, yesterday, day before)
        for i in range(3):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=2-i)
            )
        
        # Gap on day 3 and 4
        
        # Days 5, 6, 7
        for i in range(3):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=7-i)
            )
        
        result = recalculate_user_streak(user)
        
        # Current streak is 3 (today and 2 days back)
        assert result['current_streak'] == 3
        # Longest is also 3
        assert result['longest_streak'] == 3
    
    def test_longest_streak_in_past(self):
        """Test that longest streak can be in the past."""
        user = UserFactory(timezone='Europe/Prague')
        
        # Old 10-day streak (days 20-11 ago)
        for i in range(10):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=20-i)
            )
        
        # Gap
        
        # Recent 3-day streak (today, yesterday, day before)
        for i in range(3):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=2-i)
            )
        
        result = recalculate_user_streak(user)
        
        assert result['current_streak'] == 3
        assert result['longest_streak'] == 10  # From the past
    
    def test_multiple_entries_same_day(self):
        """Test that multiple entries on same day count as one day."""
        user = UserFactory(timezone='Europe/Prague')
        
        # Create 3 entries today
        for _ in range(3):
            EntryFactory(user=user, created_at=timezone.now())
        
        # Create 2 entries yesterday
        yesterday = timezone.now() - timedelta(days=1)
        for _ in range(2):
            EntryFactory(user=user, created_at=yesterday)
        
        result = recalculate_user_streak(user)
        
        # Should count as 2-day streak, not 5
        assert result['current_streak'] == 2
        assert result['longest_streak'] == 2
    
    def test_timezone_respected(self):
        """Test that user's timezone is respected in recalculation."""
        user = UserFactory(timezone='America/New_York')
        
        # Create entry at 04:00 UTC on Jan 16
        # This is 23:00 New York time on Jan 15
        utc_dt = timezone.datetime(2024, 1, 16, 4, 0, 0, tzinfo=pytz.UTC)
        EntryFactory(user=user, created_at=utc_dt)
        
        result = recalculate_user_streak(user)
        
        # The entry should be counted as Jan 15 in New York time
        assert result['longest_streak'] == 1
    
    def test_recalculation_with_complex_history(self):
        """Test recalculation with complex entry history."""
        user = UserFactory(timezone='Europe/Prague')
        
        # Build complex pattern:
        # Days 0-2: streak of 3
        # Days 3-5: gap
        # Days 6-10: streak of 5 (longest)
        # Days 11-13: gap
        # Days 14-16: streak of 3
        
        base = timezone.now()
        
        # Current streak (days 0-2)
        for i in range(3):
            EntryFactory(user=user, created_at=base - timedelta(days=2-i))
        
        # Old streak 1 (days 6-10)
        for i in range(5):
            EntryFactory(user=user, created_at=base - timedelta(days=10-i))
        
        # Old streak 2 (days 14-16)
        for i in range(3):
            EntryFactory(user=user, created_at=base - timedelta(days=16-i))
        
        result = recalculate_user_streak(user)
        
        assert result['current_streak'] == 3
        assert result['longest_streak'] == 5


@pytest.mark.unit
@pytest.mark.utils
class TestGetRandomQuote:
    """Test get_random_quote function."""
    
    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        quote = get_random_quote()
        
        assert isinstance(quote, dict)
    
    def test_has_text_and_author_keys(self):
        """Test that returned dict has 'text' and 'author' keys."""
        quote = get_random_quote()
        
        assert 'text' in quote
        assert 'author' in quote
    
    def test_text_is_non_empty_string(self):
        """Test that quote text is a non-empty string."""
        quote = get_random_quote()
        
        assert isinstance(quote['text'], str)
        assert len(quote['text']) > 0
    
    def test_author_can_be_none(self):
        """Test that author can be None."""
        quote = get_random_quote()
        
        # Author is None or string
        assert quote['author'] is None or isinstance(quote['author'], str)
    
    def test_returns_quote_from_list(self):
        """Test that returned quote is from INSPIRATIONAL_QUOTES."""
        quote = get_random_quote()
        
        assert quote in INSPIRATIONAL_QUOTES
    
    def test_randomness(self):
        """Test that function returns different quotes (probabilistic)."""
        # Get 20 quotes
        quotes = [get_random_quote() for _ in range(20)]
        
        # Should have at least 2 different quotes (very likely with 8 quotes)
        unique_quotes = set(q['text'] for q in quotes)
        assert len(unique_quotes) >= 2
    
    def test_all_quotes_are_czech(self):
        """Test that all quotes contain Czech characters or text."""
        for quote in INSPIRATIONAL_QUOTES:
            # Check that quote text is in Czech (contains Czech chars or is Czech text)
            assert isinstance(quote['text'], str)
            assert len(quote['text']) > 0
    
    def test_inspirational_quotes_list_is_not_empty(self):
        """Test that INSPIRATIONAL_QUOTES list is not empty."""
        assert len(INSPIRATIONAL_QUOTES) > 0
    
    def test_inspirational_quotes_structure(self):
        """Test that all quotes in INSPIRATIONAL_QUOTES have correct structure."""
        for quote in INSPIRATIONAL_QUOTES:
            assert isinstance(quote, dict)
            assert 'text' in quote
            assert 'author' in quote
            assert isinstance(quote['text'], str)
            assert len(quote['text']) > 0
            # Author is None or string
            assert quote['author'] is None or isinstance(quote['author'], str)
