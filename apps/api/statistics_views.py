"""
Statistics views for QuietPage.

This module contains API views for calculating and serving
journal statistics including mood trends and word count analytics
across different time periods.
"""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Count
from django.utils import timezone

from apps.journal.models import Entry

logger = logging.getLogger(__name__)


class StatisticsView(APIView):
    """
    API endpoint for journal statistics and analytics.

    Returns aggregated statistics for a specified time period:
        - period: Time period (week, month, year)
        - mood_analytics: Mood trends (average, distribution, daily breakdown)
        - word_count_analytics: Word count stats (total, average, daily breakdown)

    Query Parameters:
        - period: Time period ('week', 'month', 'year'). Defaults to 'week'

    Authentication:
        - Requires authenticated user (IsAuthenticated)

    Caching:
        - Results are cached for 5 minutes to reduce database load
    """
    permission_classes = [IsAuthenticated]

    def _get_period_range(self, user, period):
        """
        Calculate date range for a given time period in user's timezone.

        Args:
            user: User object with timezone field
            period: String ('week', 'month', 'year')

        Returns:
            tuple: (start_date, end_date) as timezone-aware datetime objects

        Raises:
            ValueError: If period is invalid
        """
        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)

        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:
            raise ValueError(f"Invalid period: {period}")

        end_date = now
        return start_date, end_date

    def _calculate_mood_analytics(self, user, start_date, end_date):
        """
        Calculate mood analytics for a date range.

        Returns:
            dict: Mood statistics including:
                - average: Average mood rating (1-5)
                - distribution: Count of entries per mood rating (1-5)
                - daily_breakdown: List of daily mood averages
                - total_rated_entries: Total entries with mood ratings
        """
        queryset = Entry.objects.filter(
            user=user,
            created_at__gte=start_date,
            created_at__lte=end_date,
            mood_rating__isnull=False
        )

        total_rated = queryset.count()

        if total_rated == 0:
            return {
                'average': None,
                'distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'daily_breakdown': [],
                'total_rated_entries': 0
            }

        average = queryset.aggregate(avg=Avg('mood_rating'))['avg']

        distribution = {}
        for rating in range(1, 6):
            distribution[rating] = queryset.filter(mood_rating=rating).count()

        daily_breakdown = []
        current_date = start_date.date()
        end_date_local = end_date.date()

        while current_date <= end_date_local:
            day_start = datetime.combine(current_date, datetime.min.time()).replace(tzinfo=start_date.tzinfo)
            day_end = datetime.combine(current_date, datetime.max.time()).replace(tzinfo=start_date.tzinfo)

            day_avg = queryset.filter(
                created_at__gte=day_start,
                created_at__lte=day_end
            ).aggregate(avg=Avg('mood_rating'))['avg']

            daily_breakdown.append({
                'date': current_date.isoformat(),
                'average': round(day_avg, 2) if day_avg else None
            })

            current_date += timedelta(days=1)

        return {
            'average': round(average, 2) if average else None,
            'distribution': distribution,
            'daily_breakdown': daily_breakdown,
            'total_rated_entries': total_rated
        }

    def _calculate_word_count_analytics(self, user, start_date, end_date):
        """
        Calculate word count analytics for a date range.

        Returns:
            dict: Word count statistics including:
                - total: Total words written
                - average: Average words per entry
                - daily_breakdown: List of daily word counts
                - total_entries: Total entries in period
        """
        queryset = Entry.objects.filter(
            user=user,
            created_at__gte=start_date,
            created_at__lte=end_date
        )

        total_words = queryset.aggregate(total=Sum('word_count'))['total'] or 0
        total_entries = queryset.count()

        average = total_words / total_entries if total_entries > 0 else 0

        daily_breakdown = []
        current_date = start_date.date()
        end_date_local = end_date.date()

        while current_date <= end_date_local:
            day_start = datetime.combine(current_date, datetime.min.time()).replace(tzinfo=start_date.tzinfo)
            day_end = datetime.combine(current_date, datetime.max.time()).replace(tzinfo=start_date.tzinfo)

            day_total = queryset.filter(
                created_at__gte=day_start,
                created_at__lte=day_end
            ).aggregate(total=Sum('word_count'))['total'] or 0

            daily_breakdown.append({
                'date': current_date.isoformat(),
                'word_count': day_total
            })

            current_date += timedelta(days=1)

        return {
            'total': total_words,
            'average': round(average, 2),
            'daily_breakdown': daily_breakdown,
            'total_entries': total_entries
        }

    def get(self, request):
        """
        Get statistics for the current user.

        Query Parameters:
            - period: Time period ('week', 'month', 'year'). Defaults to 'week'

        Returns:
            Response with statistics data:
                - period: Requested period
                - mood_analytics: Mood trends data
                - word_count_analytics: Word count data
        """
        user = request.user
        period = request.query_params.get('period', 'week')

        valid_periods = ['week', 'month', 'year']
        if period not in valid_periods:
            return Response({
                'error': f'Invalid period. Must be one of: {", ".join(valid_periods)}'
            }, status=400)

        try:
            start_date, end_date = self._get_period_range(user, period)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

        mood_analytics = self._calculate_mood_analytics(user, start_date, end_date)
        word_count_analytics = self._calculate_word_count_analytics(user, start_date, end_date)

        return Response({
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'mood_analytics': mood_analytics,
            'word_count_analytics': word_count_analytics
        })
