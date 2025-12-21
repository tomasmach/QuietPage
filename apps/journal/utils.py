"""
Utility functions for journal app.

Includes streak calculation and timezone handling.
"""

from datetime import timedelta
import pytz
from django.utils import timezone


def get_user_local_date(utc_datetime, user_timezone):
    """
    Convert UTC datetime to user's local date.
    
    Args:
        utc_datetime: Timezone-aware datetime in UTC
        user_timezone: User's timezone string (e.g., 'Europe/Prague')
    
    Returns:
        date object in user's local timezone
    """
    tz = pytz.timezone(str(user_timezone))
    local_dt = utc_datetime.astimezone(tz)
    return local_dt.date()


def update_user_streak(user, entry_created_at):
    """
    Update user's writing streak when new entry is created.
    
    Logic:
    - First entry ever: streak = 1
    - Same day entry: no change
    - Consecutive day: increment streak
    - Gap detected: reset to 1
    
    Args:
        user: User instance
        entry_created_at: DateTime when entry was created (UTC)
    """
    # Convert to user's local date
    entry_date = get_user_local_date(entry_created_at, user.timezone)
    
    if user.last_entry_date is None:
        # First entry ever
        user.current_streak = 1
        user.longest_streak = 1
    elif entry_date == user.last_entry_date:
        # Same day - multiple entries don't extend streak
        return  # No update needed
    elif entry_date == user.last_entry_date + timedelta(days=1):
        # Consecutive day - increment streak
        user.current_streak += 1
        # Update longest if we broke the record
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
    else:
        # Gap detected - streak broken
        user.current_streak = 1
    
    # Update last entry date
    user.last_entry_date = entry_date
    user.save(update_fields=['current_streak', 'longest_streak', 'last_entry_date'])


def recalculate_user_streak(user):
    """
    Recalculate streak from scratch based on entry history.
    
    Useful for:
    - Data verification
    - Fixing corrupted streak data
    - Admin tools
    
    Returns:
        dict with current_streak and longest_streak
    """
    from .models import Entry
    
    entries = Entry.objects.filter(user=user).order_by('created_at')
    
    if not entries.exists():
        return {'current_streak': 0, 'longest_streak': 0}
    
    # Get all unique dates (in user's timezone)
    dates = sorted(set(
        get_user_local_date(entry.created_at, user.timezone)
        for entry in entries
    ))
    
    # Calculate current streak (working backwards from today)
    today = get_user_local_date(timezone.now(), user.timezone)
    current_streak = 0
    
    for i in range(len(dates) - 1, -1, -1):
        expected_date = today - timedelta(days=current_streak)
        if dates[i] == expected_date:
            current_streak += 1
        else:
            break
    
    # Calculate longest streak (scan through all dates)
    longest_streak = 1
    temp_streak = 1
    
    for i in range(1, len(dates)):
        if dates[i] - dates[i-1] == timedelta(days=1):
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak
    }
