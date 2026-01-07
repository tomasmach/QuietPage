"""
Statistics views for QuietPage.

This module contains API views for calculating and serving
journal statistics including mood trends and word count analytics
across different time periods.
"""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from django.db.models import Sum, Avg, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator

from apps.journal.models import Entry
from apps.api.serializers import StatisticsSerializer

logger = logging.getLogger(__name__)


def custom_cache_key(request):
    """
    Generate cache key for statistics endpoint.
    
    Note: cache_page decorator passes a standard Django HttpRequest,
    not DRF's Request wrapper, so we use request.GET instead of query_params.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        str: Cache key in format 'statistics_{user_id}_{period}_{last_entry_date}'
    """
    user = request.user
    period = request.GET.get("period", "7d")
    last_entry_date = (
        user.last_entry_date.isoformat() if user.last_entry_date else "none"
    )
    return f"statistics_{user.id}_{period}_{last_entry_date}"


class StatisticsView(APIView):
    """
    API endpoint for journal statistics and analytics.

    Returns aggregated statistics for a specified time period:
        - period: Time period (7d, 30d, 90d, 1y, all)
        - mood_analytics: Mood trends (average, distribution, daily breakdown)
        - word_count_analytics: Word count stats (total, average, daily breakdown)
        - writing_patterns: Consistency, time-of-day, day-of-week, streak history
        - tag_analytics: Tag usage statistics (entry count, words, mood per tag)
        - goal_streak: Consecutive days meeting daily word goal (current, longest, goal)

    Query Parameters:
        - period: Time period ('7d', '30d', '90d', '1y', 'all'). Defaults to '7d'

    Authentication:
        - Requires authenticated user (IsAuthenticated)

    Rate Limiting:
        - 100 requests per hour per user (prevents abuse of expensive database queries)
        - Uses ScopedRateThrottle with 'statistics' scope

    Caching:
        - Results are cached for 30 minutes using database cache backend
        - Cache key includes user.id, period, and last_entry_date for automatic invalidation
        - Client-side caching enabled via cache headers
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'statistics'

    def _normalize_to_local_day(self, dt, user_tz):
        """
        Normalize datetime to local day, handling DST transitions.
        Uses fold=0 for consistent behavior during fall-back.

        Args:
            dt: datetime object (timezone-aware or naive)
            user_tz: ZoneInfo timezone object

        Returns:
            datetime: Normalized to 00:00:00 in user's timezone with fold=0
        """
        local_dt = dt.astimezone(user_tz)
        return local_dt.replace(hour=0, minute=0, second=0, microsecond=0, fold=0)

    def _get_period_range(self, period, user):
        """
        Calculate date range for a given time period in user's timezone.

        Args:
            period: String ('7d', '30d', '90d', '1y', 'all')
            user: User object with timezone field

        Returns:
            tuple: (start_date, end_date) as timezone-aware datetime objects
                    start_date is at 00:00:00, end_date is at 23:59:59

        Raises:
            ValueError: If period is invalid
        """
        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)

        if period == "7d":
            start_date = now - timedelta(days=7)
        elif period == "30d":
            start_date = now - timedelta(days=30)
        elif period == "90d":
            start_date = now - timedelta(days=90)
        elif period == "1y":
            start_date = now - relativedelta(years=1)
        elif period == "all":
            first_entry = Entry.objects.filter(user=user).order_by("created_at").first()
            if first_entry:
                start_date = first_entry.created_at.astimezone(user_tz)
            else:
                start_date = now
        else:
            raise ValueError(f"Invalid period: {period}")

        start_date = self._normalize_to_local_day(start_date, user_tz)
        end_date = now.replace(
            hour=23, minute=59, second=59, microsecond=999999, fold=0
        )

        return start_date, end_date

    def _categorize_time_of_day(self, hour: int) -> str:
        """
        Categorize hour into time-of-day category.

        Args:
            hour: Hour of day (0-23)

        Returns:
            str: Time of day category ('morning', 'afternoon', 'evening', 'night')
        """
        if 5 <= hour <= 11:
            return 'morning'
        elif 12 <= hour <= 17:
            return 'afternoon'
        elif 18 <= hour <= 23:
            return 'evening'
        else:
            return 'night'

    def _calculate_mood_analytics(self, entries, period_start, user_tz):
        """
        Calculate mood analytics for a filtered entries queryset.

        Args:
            entries: QuerySet of Entry objects already filtered by user and date range
            period_start: Start datetime of the period (for trend calculation)
            user_tz: ZoneInfo timezone object for the user

        Returns:
            dict: Mood statistics including:
                - average: Average mood rating (1-5)
                - distribution: Count of entries per mood rating (1-5)
                - timeline: List of daily mood averages with dates
                - total_rated_entries: Total entries with mood ratings
                - trend: 'improving', 'declining', or 'stable'
        """
        rated_entries = entries.filter(mood_rating__isnull=False)
        total_rated = rated_entries.count()

        if total_rated == 0:
            return {
                "average": None,
                "distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                "timeline": [],
                "total_rated_entries": 0,
                "trend": "stable",
            }

        average = rated_entries.aggregate(avg=Avg("mood_rating"))["avg"]

        distribution = {}
        for rating in range(1, 6):
            distribution[str(rating)] = rated_entries.filter(mood_rating=rating).count()

        daily_data = (
            rated_entries.annotate(day=TruncDate("created_at", tzinfo=user_tz))
            .values("day")
            .annotate(
                avg_mood=Avg("mood_rating", filter=Q(mood_rating__isnull=False)),
                count=Count("id", filter=Q(mood_rating__isnull=False)),
            )
            .order_by("day")
        )

        timeline = []
        for item in daily_data:
            timeline.append(
                {
                    "date": item["day"].isoformat(),
                    "average": round(item["avg_mood"], 2) if item["avg_mood"] else None,
                    "count": item["count"],
                }
            )

        if len(timeline) >= 2:
            midpoint = len(timeline) // 2
            first_half_values = [
                day["average"]
                for day in timeline[:midpoint]
                if day["average"] is not None
            ]
            second_half_values = [
                day["average"]
                for day in timeline[midpoint:]
                if day["average"] is not None
            ]

            if first_half_values and second_half_values:
                first_half_avg = sum(first_half_values) / len(first_half_values)
                second_half_avg = sum(second_half_values) / len(second_half_values)

                if second_half_avg - first_half_avg > 0.3:
                    trend = "improving"
                elif first_half_avg - second_half_avg > 0.3:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "average": round(average, 2) if average else None,
            "distribution": distribution,
            "timeline": timeline,
            "total_rated_entries": total_rated,
            "trend": trend,
        }

    def _calculate_word_count_analytics(self, entries, user, period_start, user_tz):
        """
        Calculate word count analytics for a filtered entries queryset.

        Args:
            entries: QuerySet of Entry objects already filtered by user and date range
            user: User object for daily_word_goal reference
            period_start: Start datetime of the period (not directly used, kept for consistency)
            user_tz: ZoneInfo timezone object for the user

        Returns:
            dict: Word count statistics including:
                - total: Total words written
                - average_per_entry: Average words per entry
                - average_per_day: Average words per day (active days only)
                - timeline: List of daily word counts with dates
                - total_entries: Total entries in period
                - goal_achievement_rate: Percentage of active days meeting daily goal
                - best_day: Best writing day with word count
        """
        total_words = entries.aggregate(total=Sum("word_count"))["total"] or 0
        total_entries = entries.count()

        average_per_entry = total_words / total_entries if total_entries > 0 else 0

        daily_data = (
            entries.annotate(day=TruncDate("created_at", tzinfo=user_tz))
            .values("day")
            .annotate(total_words=Sum("word_count"), entries=Count("id"))
            .order_by("day")
        )

        timeline = []
        active_days_count = 0
        days_meeting_goal = 0
        best_day = None
        max_words = 0

        for item in daily_data:
            timeline.append(
                {
                    "date": item["day"].isoformat(),
                    "word_count": item["total_words"],
                    "entry_count": item["entries"],
                }
            )

            active_days_count += 1
            if item["total_words"] >= user.daily_word_goal:
                days_meeting_goal += 1

            if item["total_words"] > max_words:
                max_words = item["total_words"]
                best_day = {
                    "date": item["day"].isoformat(),
                    "word_count": item["total_words"],
                    "entry_count": item["entries"],
                }

        average_per_day = (
            total_words / active_days_count if active_days_count > 0 else 0
        )

        goal_achievement_rate = (
            (days_meeting_goal / active_days_count * 100)
            if active_days_count > 0
            else 0
        )

        return {
            "total": total_words,
            "average_per_entry": round(average_per_entry, 2),
            "average_per_day": round(average_per_day, 2),
            "timeline": timeline,
            "total_entries": total_entries,
            "goal_achievement_rate": round(goal_achievement_rate, 2),
            "best_day": best_day,
        }

    def _calculate_writing_patterns(self, entries, user, start_date, end_date):
        """
        Calculate writing patterns including consistency, time-of-day distribution,
        day-of-week distribution, and streak history.

        Args:
            entries: QuerySet of Entry objects already filtered by user and date range
            user: User object with timezone field
            start_date: Start datetime of the requested period
            end_date: End datetime of the requested period

        Returns:
            dict: Writing patterns statistics including:
                - consistency_rate: Percentage of days with entries (active_days / total_days)
                - time_of_day: Distribution of entries by time of day (morning/afternoon/evening/night)
                - day_of_week: Distribution of entries by day of week (Monday-Sunday)
                - streak_history: Top 5 longest streaks with start_date, end_date, and length
        """
        if not entries.exists():
            return {
                "consistency_rate": 0.0,
                "time_of_day": {"morning": 0, "afternoon": 0, "evening": 0, "night": 0},
                "day_of_week": {
                    "monday": 0,
                    "tuesday": 0,
                    "wednesday": 0,
                    "thursday": 0,
                    "friday": 0,
                    "saturday": 0,
                    "sunday": 0,
                },
                "streak_history": [],
            }

        user_tz = ZoneInfo(str(user.timezone))

        # Calculate total days in the requested period
        start_date_normalized = self._normalize_to_local_day(start_date, user_tz)
        end_date_normalized = self._normalize_to_local_day(end_date, user_tz)
        total_days = (end_date_normalized - start_date_normalized).days + 1

        # Only count days with actual writing (word_count > 0) for consistency
        # with streak calculation logic in signals.py
        active_days = (
            entries.filter(word_count__gt=0)
            .annotate(day=TruncDate("created_at", tzinfo=user_tz))
            .values("day")
            .distinct()
            .count()
        )

        consistency_rate = (active_days / total_days * 100) if total_days > 0 else 0.0

        # Filter entries with actual content for writing pattern analysis
        entries_with_content = entries.filter(word_count__gt=0)

        time_of_day = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
        for entry in entries_with_content.only('created_at'):
            local_time = entry.created_at.astimezone(user_tz)
            hour = local_time.hour
            category = self._categorize_time_of_day(hour)
            time_of_day[category] += 1

        day_of_week_dist = (
            entries_with_content.values("created_at__week_day")
            .annotate(count=Count("id"))
            .order_by("created_at__week_day")
        )

        day_names = {
            1: "sunday",
            2: "monday",
            3: "tuesday",
            4: "wednesday",
            5: "thursday",
            6: "friday",
            7: "saturday",
        }

        day_of_week = {
            "monday": 0,
            "tuesday": 0,
            "wednesday": 0,
            "thursday": 0,
            "friday": 0,
            "saturday": 0,
            "sunday": 0,
        }

        for item in day_of_week_dist:
            week_day = item["created_at__week_day"]
            count = item["count"]
            if week_day in day_names:
                day_of_week[day_names[week_day]] = count

        # Group entries with content by day for streak calculation
        # Since we've already filtered by word_count > 0, all days will have total_words > 0
        daily_entries = (
            entries_with_content.annotate(day=TruncDate("created_at", tzinfo=user_tz))
            .values("day")
            .annotate(
                total_words=Sum("word_count"),
                entries=Count("id"),
            )
            .order_by("day")
        )

        writing_days = []
        for item in daily_entries:
            # Already filtered by word_count > 0, but keep check for safety
            if item["total_words"] and item["total_words"] > 0:
                writing_days.append(item["day"])

        streaks = []
        if writing_days:
            current_streak_start = writing_days[0]
            current_streak_end = writing_days[0]

            for i in range(1, len(writing_days)):
                prev_day = writing_days[i - 1]
                current_day = writing_days[i]

                if (current_day - prev_day).days == 1:
                    current_streak_end = current_day
                else:
                    streak_length = (current_streak_end - current_streak_start).days + 1
                    streaks.append(
                        {
                            "start_date": current_streak_start.isoformat(),
                            "end_date": current_streak_end.isoformat(),
                            "length": streak_length,
                        }
                    )
                    current_streak_start = current_day
                    current_streak_end = current_day

            streak_length = (current_streak_end - current_streak_start).days + 1
            streaks.append(
                {
                    "start_date": current_streak_start.isoformat(),
                    "end_date": current_streak_end.isoformat(),
                    "length": streak_length,
                }
            )

        streak_history = sorted(streaks, key=lambda x: x["length"], reverse=True)[:5]

        return {
            "consistency_rate": round(consistency_rate, 2),
            "time_of_day": time_of_day,
            "day_of_week": day_of_week,
            "streak_history": streak_history,
        }

    def _calculate_milestones(self, user, all_entries):
        """
        Calculate achievement milestones for the user.

        Milestones are calculated based on ALL user data, not filtered by period.
        This provides a consistent view of user achievements regardless of the
        selected time period in the statistics view.

        Args:
            user: User object with streak fields (current_streak, longest_streak)
            all_entries: QuerySet of ALL Entry objects for the user (not period-filtered)

        Returns:
            dict: Milestones data including:
                - milestones: List of milestone objects with:
                    - type: 'entries', 'words', or 'streak'
                    - value: Milestone threshold value
                    - achieved: Boolean indicating if user reached this milestone
                    - current: User's current value for this milestone type
            Labels are handled by frontend i18n based on type and value.
        """
        # Define milestone thresholds
        entry_milestones = [1, 10, 50, 100, 365, 500, 1000]
        word_milestones = [1000, 10000, 50000, 100000, 250000, 500000, 1000000]
        streak_milestones = [7, 30, 100, 365]

        # Calculate current values
        total_entries = all_entries.count()
        total_words = all_entries.aggregate(total=Sum("word_count"))["total"] or 0
        longest_streak = user.longest_streak

        milestones = []

        # Entry milestones
        for value in entry_milestones:
            milestones.append({
                "type": "entries",
                "value": value,
                "achieved": total_entries >= value,
                "current": total_entries,
            })

        # Word milestones
        for value in word_milestones:
            milestones.append({
                "type": "words",
                "value": value,
                "achieved": total_words >= value,
                "current": total_words,
            })

        # Streak milestones (based on longest_streak from User model)
        for value in streak_milestones:
            milestones.append({
                "type": "streak",
                "value": value,
                "achieved": longest_streak >= value,
                "current": longest_streak,
            })

        return {"milestones": milestones}

    def _calculate_personal_records(self, user, all_entries, goal_streak_data):
        """
        Calculate all-time personal records for the user.

        Personal records are calculated based on ALL user data, not filtered by period.
        This gives users goals to beat and celebrates past achievements.

        Args:
            user: User object with longest_streak field
            all_entries: QuerySet of ALL Entry objects for the user (not period-filtered)
            goal_streak_data: Result from _calculate_goal_streak() for longest_goal_streak

        Returns:
            dict: Personal records including:
                - longest_entry: Entry with highest word_count
                    - date: ISO date string
                    - word_count: Number of words
                    - title: Entry title (if exists, else null)
                    - entry_id: UUID of the entry
                - most_words_in_day: Day with highest total words
                    - date: ISO date string
                    - word_count: Total words that day
                    - entry_count: Number of entries that day
                - longest_streak: User's all-time longest streak (from User model)
                - longest_goal_streak: All-time longest goal streak
        """
        user_tz = ZoneInfo(str(user.timezone))

        # Longest entry (single entry with most words)
        longest_entry_record = None
        longest_entry = (
            all_entries.filter(word_count__gt=0)
            .order_by("-word_count")
            .first()
        )
        if longest_entry:
            longest_entry_record = {
                "date": longest_entry.created_at.astimezone(user_tz).date().isoformat(),
                "word_count": longest_entry.word_count,
                "title": longest_entry.title if longest_entry.title else None,
                "entry_id": str(longest_entry.id),
            }

        # Most words in a single day (sum of all entries that day)
        most_words_in_day_record = None
        daily_totals = (
            all_entries.filter(word_count__gt=0)
            .annotate(day=TruncDate("created_at", tzinfo=user_tz))
            .values("day")
            .annotate(
                total_words=Sum("word_count"),
                entry_count=Count("id"),
            )
            .order_by("-total_words")
            .first()
        )
        if daily_totals:
            most_words_in_day_record = {
                "date": daily_totals["day"].isoformat(),
                "word_count": daily_totals["total_words"],
                "entry_count": daily_totals["entry_count"],
            }

        return {
            "longest_entry": longest_entry_record,
            "most_words_in_day": most_words_in_day_record,
            "longest_streak": user.longest_streak,
            "longest_goal_streak": goal_streak_data["longest"],
        }

    def _calculate_goal_streak(self, user):
        """
        Calculate goal streak - consecutive days meeting daily word goal.

        Unlike regular streak (any entry with content), goal streak tracks
        consecutive days where the user's total word count >= daily_word_goal.

        Args:
            user: User object with timezone and daily_word_goal fields

        Returns:
            dict: Goal streak statistics including:
                - current: Current consecutive days meeting goal (ending today or yesterday)
                - longest: All-time longest goal streak
                - goal: User's daily_word_goal for reference
        """
        from apps.journal.models import Entry

        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        today = now.date()
        yesterday = today - timedelta(days=1)

        # Get all entries with content, grouped by day with total word count
        daily_totals = (
            Entry.objects.filter(user=user, word_count__gt=0)
            .annotate(day=TruncDate("created_at", tzinfo=user_tz))
            .values("day")
            .annotate(total_words=Sum("word_count"))
            .order_by("day")
        )

        # Filter to only days meeting the goal
        goal_days = sorted([
            item["day"]
            for item in daily_totals
            if item["total_words"] >= user.daily_word_goal
        ])

        if not goal_days:
            return {
                "current": 0,
                "longest": 0,
                "goal": user.daily_word_goal,
            }

        # Calculate current goal streak (working backwards from today/yesterday)
        current_streak = 0
        
        # Check if streak is still active (last goal day is today or yesterday)
        last_goal_day = goal_days[-1]
        if last_goal_day == today or last_goal_day == yesterday:
            # Count consecutive days backwards from the last goal day
            current_streak = 1
            for i in range(len(goal_days) - 2, -1, -1):
                expected_date = last_goal_day - timedelta(days=current_streak)
                if goal_days[i] == expected_date:
                    current_streak += 1
                else:
                    break

        # Calculate longest goal streak (scan through all goal days)
        longest_streak = 1 if goal_days else 0
        temp_streak = 1

        for i in range(1, len(goal_days)):
            if goal_days[i] - goal_days[i - 1] == timedelta(days=1):
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1

        return {
            "current": current_streak,
            "longest": longest_streak,
            "goal": user.daily_word_goal,
        }

    def _calculate_tag_analytics(self, entries):
        """
        Calculate tag analytics for a filtered entries queryset.

        Args:
            entries: QuerySet of Entry objects already filtered by user and date range

        Returns:
            dict: Tag statistics including:
                - tags: List of tag objects with statistics:
                    - name: Tag name
                    - entry_count: Number of entries with this tag
                    - total_words: Total words written in entries with this tag
                    - average_words: Average words per entry with this tag
                    - average_mood: Average mood rating for entries with this tag (null if no ratings)
                - total_tags: Total number of unique tags used
        """
        if not entries.exists():
            return {
                "tags": [],
                "total_tags": 0,
            }

        # Get all tags used in the filtered entries
        # Use django-taggit's prefetch to efficiently get tag data
        tag_stats = {}
        
        # Prefetch tags for efficiency
        entries_with_tags = entries.prefetch_related('tags')
        
        for entry in entries_with_tags:
            for tag in entry.tags.all():
                if tag.name not in tag_stats:
                    tag_stats[tag.name] = {
                        "entry_count": 0,
                        "total_words": 0,
                        "mood_ratings": [],
                    }
                
                tag_stats[tag.name]["entry_count"] += 1
                tag_stats[tag.name]["total_words"] += entry.word_count
                if entry.mood_rating is not None:
                    tag_stats[tag.name]["mood_ratings"].append(entry.mood_rating)

        # Calculate averages and format output
        tags_list = []
        for tag_name, stats in tag_stats.items():
            average_words = (
                stats["total_words"] / stats["entry_count"]
                if stats["entry_count"] > 0
                else 0
            )
            
            average_mood = None
            if stats["mood_ratings"]:
                average_mood = round(
                    sum(stats["mood_ratings"]) / len(stats["mood_ratings"]), 2
                )
            
            tags_list.append({
                "name": tag_name,
                "entry_count": stats["entry_count"],
                "total_words": stats["total_words"],
                "average_words": round(average_words, 2),
                "average_mood": average_mood,
            })

        # Sort by entry count (most used tags first)
        tags_list.sort(key=lambda x: x["entry_count"], reverse=True)

        return {
            "tags": tags_list,
            "total_tags": len(tags_list),
        }

    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(cache_page(1800, key_prefix=custom_cache_key))
    def get(self, request):
        """
        Get statistics for the current user.

        Query Parameters:
            - period: Time period ('7d', '30d', '90d', '1y', 'all'). Defaults to '7d'

        Returns:
            Response with statistics data:
                - period: Requested period
                - start_date: Start date of period (ISO format)
                - end_date: End date of period (ISO format)
                - mood_analytics: Mood trends data
                - word_count_analytics: Word count data
                - writing_patterns: Writing habits and consistency data
                - tag_analytics: Tag usage statistics
                - milestones: Achievement milestones (based on ALL user data)
                - goal_streak: Consecutive days meeting daily word goal (all-time)
                - personal_records: All-time personal records (longest entry, most words in day, etc.)

        Caching:
            - Server-side: 30 minutes (1800 seconds)
            - Client-side: Controlled by Cache-Control headers
            - Cache key: statistics_{user.id}_{period}_{last_entry_date}
            - Automatic invalidation: last_entry_date changes on new entry creation
        """
        user = request.user
        period = request.query_params.get("period", "7d")

        valid_periods = ["7d", "30d", "90d", "1y", "all"]
        if period not in valid_periods:
            return Response(
                {
                    "error": f'Invalid period. Must be one of: {", ".join(valid_periods)}'
                },
                status=400,
            )

        try:
            start_date, end_date = self._get_period_range(period, user)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        user_tz = ZoneInfo(str(user.timezone))
        entries = Entry.objects.filter(
            user=user, created_at__gte=start_date, created_at__lte=end_date
        )

        # Get ALL entries for milestone calculation (not period-filtered)
        all_entries = Entry.objects.filter(user=user)

        mood_analytics = self._calculate_mood_analytics(entries, start_date, user_tz)
        word_count_analytics = self._calculate_word_count_analytics(
            entries, user, start_date, user_tz
        )
        writing_patterns = self._calculate_writing_patterns(entries, user, start_date, end_date)
        tag_analytics = self._calculate_tag_analytics(entries)
        milestones = self._calculate_milestones(user, all_entries)
        goal_streak = self._calculate_goal_streak(user)
        personal_records = self._calculate_personal_records(user, all_entries, goal_streak)

        data = {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "mood_analytics": mood_analytics,
            "word_count_analytics": word_count_analytics,
            "writing_patterns": writing_patterns,
            "tag_analytics": tag_analytics,
            "milestones": milestones,
            "goal_streak": goal_streak,
            "personal_records": personal_records,
        }
        serializer = StatisticsSerializer(data)
        return Response(serializer.data)
