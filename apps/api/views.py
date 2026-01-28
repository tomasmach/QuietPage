"""
API views for QuietPage.

This module contains ViewSets and API views for handling REST requests
for journal entries, dashboard data, and autosave functionality.
"""

import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from django.db.models import Sum, Count, Q
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone

from apps.journal.models import Entry, FeaturedEntry
from apps.journal.utils import (
    get_random_quote,
    get_user_local_date,
    get_today_date_range,
    parse_tags,
    recalculate_user_streak,
)
from apps.api.serializers import (
    EntrySerializer,
    EntryListSerializer,
    DashboardStatsSerializer,
)

logger = logging.getLogger(__name__)


class EntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for journal entry operations.

    Provides full CRUD operations for journal entries with user isolation.
    Uses different serializers for list (without content) and detail views.
    """
    permission_classes = [IsAuthenticated]
    throttle_scope = 'entries_create'

    def get_throttles(self):
        """
        Apply throttling only on create action to prevent spam.
        Other actions (list, retrieve, update, delete) are not throttled.
        """
        if self.action == 'create':
            return [ScopedRateThrottle()]
        return super().get_throttles()

    def get_queryset(self):
        """
        Filter entries to show only current user's entries.

        Ordered by most recent first for consistent listing.
        Uses select_related/prefetch_related for optimization.
        """
        return Entry.objects.filter(
            user=self.request.user
        ).prefetch_related('tags').order_by('-created_at')

    def get_serializer_class(self):
        """
        Use different serializers based on action.

        - list: EntryListSerializer (excludes content for performance)
        - retrieve/create/update/partial_update: EntrySerializer (includes content)
        """
        if self.action == 'list':
            return EntryListSerializer
        return EntrySerializer

    def perform_create(self, serializer):
        """
        Create entry and associate it with the authenticated user.

        The user is automatically set from the request context.
        """
        serializer.save(user=self.request.user)


class DashboardView(APIView):
    """
    API endpoint for dashboard data.

    Returns:
        - greeting: Time-based greeting (Dobré ráno/odpoledne/večer)
        - stats: User statistics (today_words, daily_goal, total_entries, current_streak, longest_streak, total_words)
        - recent_entries: Last 5 entries (without content)
        - quote: Random inspirational quote
    """
    permission_classes = [IsAuthenticated]

    def get_greeting(self, user):
        """
        Return time-based greeting in Czech.

        Time ranges:
        - 4-9: Dobré ráno
        - 9-12: Dobré dopoledne
        - 12-18: Dobré odpoledne
        - 18-4: Dobrý večer
        """
        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        hour = now.hour

        if 4 <= hour < 9:
            return "Dobré ráno"
        elif 9 <= hour < 12:
            return "Dobré dopoledne"
        elif 12 <= hour < 18:
            return "Dobré odpoledne"
        else:  # 18-4
            return "Dobrý večer"

    def get_user_today(self, user):
        """Get today's date in user's timezone."""
        user_tz = ZoneInfo(str(user.timezone))
        return timezone.now().astimezone(user_tz).date()

    def get_featured_entry(self, user, user_date):
        """
        Get or create today's featured entry for user.
        Returns None if user has < 10 entries.
        Excludes today's entries from selection.
        """
        entry_count = Entry.objects.filter(user=user).count()
        if entry_count < 10:
            return None

        with transaction.atomic():
            featured = FeaturedEntry.objects.filter(
                user=user,
                date=user_date
            ).select_for_update().select_related('entry').first()

            if featured:
                return featured.entry

            user_tz = ZoneInfo(str(user.timezone))
            now = timezone.now().astimezone(user_tz)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            random_entry = Entry.objects.filter(
                user=user
            ).exclude(
                created_at__gte=today_start
            ).order_by('?').first()

            if not random_entry:
                return None

            featured, created = FeaturedEntry.objects.get_or_create(
                user=user,
                date=user_date,
                defaults={'entry': random_entry}
            )

            return featured.entry

    def get_weekly_stats(self, user):
        """Calculate statistics for the last 7 days."""
        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)

        week_ago = (now - timedelta(days=7)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        weekly_entries = Entry.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).values('created_at', 'word_count')

        total_words = 0
        daily_words = {}

        for entry in weekly_entries:
            total_words += entry['word_count']
            entry_date = entry['created_at'].astimezone(user_tz).date()
            daily_words[entry_date] = daily_words.get(entry_date, 0) + entry['word_count']

        best_day = None
        if daily_words:
            best_date = max(daily_words, key=daily_words.get)
            weekday_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            best_day = {
                'date': best_date.isoformat(),
                'words': daily_words[best_date],
                'weekday': weekday_names[best_date.weekday()]
            }

        return {
            'total_words': total_words,
            'best_day': best_day
        }

    def serialize_featured_entry(self, entry, user_date):
        """Serialize featured entry for API response."""
        if not entry:
            return None

        user_tz = ZoneInfo(str(self.request.user.timezone))
        entry_date = entry.created_at.astimezone(user_tz).date()
        days_ago = (user_date - entry_date).days

        # Use get_content() to get decrypted content
        content = entry.get_content()
        content_preview = content[:200] if content else ''
        if content and len(content) > 200:
            content_preview += '...'

        return {
            'id': str(entry.id),
            'title': entry.title,
            'content_preview': content_preview,
            'created_at': entry.created_at.isoformat(),
            'word_count': entry.word_count,
            'days_ago': days_ago
        }

    def get(self, request):
        """
        Get dashboard data for the current user.

        Stats are cached for 5 minutes to reduce database load.
        """
        user = request.user

        # Time-based greeting
        greeting = self.get_greeting(user)

        # Recent entries - limit to 5, exclude content for performance
        recent_entries = Entry.objects.filter(
            user=user
        ).prefetch_related('tags').only(
            'id', 'title', 'created_at', 'updated_at', 'mood_rating', 'word_count'
        ).order_by('-created_at')[:5]

        # Statistics - cached for 5 minutes
        cache_key = f'dashboard_stats_{user.id}'
        stats = cache.get(cache_key)

        if not stats:
            # Calculate today's word count (in user's timezone)
            user_tz = ZoneInfo(str(user.timezone))
            now = timezone.now().astimezone(user_tz)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

            # Single aggregated query instead of 3 separate queries
            stats_aggregation = Entry.objects.filter(user=user).aggregate(
                total_entries=Count('id'),
                total_words=Sum('word_count'),
                today_words=Sum('word_count', filter=Q(
                    created_at__gte=today_start,
                    created_at__lte=today_end
                ))
            )

            # Calculate current streak in real-time (not from user model cache)
            # allow_yesterday=True keeps streak alive if user wrote yesterday
            current_streak = recalculate_user_streak(user, allow_yesterday=True)['current_streak']

            stats = {
                'today_words': stats_aggregation['today_words'] or 0,
                'daily_goal': user.daily_word_goal,
                'goal_progress': min(100, int((stats_aggregation['today_words'] or 0) / user.daily_word_goal * 100)) if user.daily_word_goal > 0 else 0,
                'current_streak': current_streak,
                'longest_streak': user.longest_streak,
                'total_entries': stats_aggregation['total_entries'] or 0,
                'total_words': stats_aggregation['total_words'] or 0,
            }
            cache.set(cache_key, stats, 300)  # Cache for 5 minutes

        # Random inspirational quote
        quote = get_random_quote()

        # Featured entry from history
        user_date = self.get_user_today(user)
        featured_entry = self.get_featured_entry(user, user_date)

        # Weekly stats
        weekly_stats = self.get_weekly_stats(user)

        return Response({
            'greeting': greeting,
            'stats': stats,
            'recent_entries': EntryListSerializer(
                recent_entries,
                many=True,
                context={'request': request}
            ).data,
            'quote': quote,
            'featured_entry': self.serialize_featured_entry(featured_entry, user_date),
            'weekly_stats': weekly_stats,
        })


class RefreshFeaturedEntryView(APIView):
    """
    API endpoint to refresh the featured entry for today.
    POST: Generates a new random featured entry (different from current).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Refresh featured entry and return new one."""
        user = request.user
        user_tz = ZoneInfo(str(user.timezone))
        user_date = timezone.now().astimezone(user_tz).date()

        entry_count = Entry.objects.filter(user=user).count()
        if entry_count < 10:
            return Response({
                'featured_entry': None,
                'message': 'Not enough entries for featured entry'
            })

        with transaction.atomic():
            current = FeaturedEntry.objects.filter(
                user=user,
                date=user_date
            ).select_for_update().first()
            exclude_ids = [current.entry_id] if current else []

            now = timezone.now().astimezone(user_tz)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            new_entry = Entry.objects.filter(
                user=user
            ).exclude(
                id__in=exclude_ids
            ).exclude(
                created_at__gte=today_start
            ).order_by('?').first()

            if not new_entry and exclude_ids:
                new_entry = Entry.objects.get(id=exclude_ids[0])

            if new_entry:
                if current:
                    current.entry = new_entry
                    current.save()
                else:
                    FeaturedEntry.objects.create(
                        user=user,
                        date=user_date,
                        entry=new_entry
                    )

        featured_data = None
        if new_entry:
            entry_date = new_entry.created_at.astimezone(user_tz).date()
            days_ago = (user_date - entry_date).days
            # Use get_content() to get decrypted content
            content = new_entry.get_content()
            content_preview = content[:200] if content else ''
            if content and len(content) > 200:
                content_preview += '...'

            featured_data = {
                'id': str(new_entry.id),
                'title': new_entry.title,
                'content_preview': content_preview,
                'created_at': new_entry.created_at.isoformat(),
                'word_count': new_entry.word_count,
                'days_ago': days_ago
            }

        return Response({
            'featured_entry': featured_data
        })


class TodayEntryView(APIView):
    """
    API endpoint pro dnešní daily note.

    GET: Vrátí dnešní záznam pokud existuje, 404 pokud ne
    POST: Vytvoří nebo updatne dnešní záznam

    Zajišťuje:
    1. Pouze jeden záznam za den (v user timezone)
    2. Záznam se vytvoří jen když je poskytnut content
    3. Streak se updatne jen při skutečném uložení contentu
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Vrátí dnešní záznam pokud existuje, jinak 404."""
        user = request.user
        today_start, today_end = get_today_date_range(user)

        try:
            entry = Entry.objects.get(
                user=user,
                created_at__gte=today_start,
                created_at__lte=today_end
            )
            serializer = EntrySerializer(entry, context={'request': request})
            return Response(serializer.data)
        except Entry.DoesNotExist:
            return Response(
                {'detail': 'Dnes ještě nemáte záznam'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Entry.MultipleObjectsReturned:
            # Legacy: více záznamů za den - vrátí nejnovější
            entry = Entry.objects.filter(
                user=user,
                created_at__gte=today_start,
                created_at__lte=today_end
            ).order_by('-created_at').first()
            serializer = EntrySerializer(entry, context={'request': request})
            return Response(serializer.data)

    def post(self, request):
        """
        Vytvoří nebo updatne dnešní záznam.

        Povolit prázdný content pro 750words.com style - jeden záznam na den.
        Streak se updatne až když entry má skutečný obsah (word_count > 0).
        """
        user = request.user
        content = (request.data.get('content') or '').strip()

        # Povolit prázdný content - entry se vytvoří, ale streak se neaktualizuje
        # (to je ošetřeno v signals.py)

        today_start, today_end = get_today_date_range(user)

        with transaction.atomic():
            entry = Entry.objects.filter(
                user=user,
                created_at__gte=today_start,
                created_at__lte=today_end
            ).select_for_update().first()

            if entry:
                # Update existujícího záznamu
                entry.title = (request.data.get('title') or '').strip()
                entry.set_content(content)
                entry.mood_rating = request.data.get('mood_rating', None)
                entry.save()

                # Update tagů
                tags_list = parse_tags(request.data.get('tags', None))
                if tags_list is not None:
                    entry.tags.set(tags_list)

                serializer = EntrySerializer(entry, context={'request': request})
                return Response(serializer.data)
            else:
                # Vytvoření nového záznamu (streak signal se spustí)
                entry = Entry(
                    user=user,
                    title=(request.data.get('title') or '').strip(),
                    mood_rating=request.data.get('mood_rating', None)
                )
                entry.set_content(content)
                entry.save()

                # Přidání tagů
                tags_list = parse_tags(request.data.get('tags', None))
                if tags_list is not None:
                    entry.tags.set(tags_list)

                serializer = EntrySerializer(entry, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)


class AutosaveView(APIView):
    """
    API endpoint for auto-saving journal entries.

    Creates a new entry or updates existing one based on entry_id.
    Uses atomic transactions with row-level locking to prevent race conditions.

    Request body:
        - entry_id (optional): UUID of existing entry to update
        - title (optional): Entry title
        - content (required): Entry content
        - mood_rating (optional): Mood rating (1-5)
        - tags (optional): Comma-separated tags or list of tags

    Response:
        - status: 'success' or 'error'
        - entry_id: UUID of the entry
        - is_new: Boolean indicating if entry was newly created
        - message: Status message
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle autosave request.

        Validates input and creates/updates entry atomically.
        """
        try:
            # Extract and validate data
            title = (request.data.get('title') or '').strip()
            content = (request.data.get('content') or '').strip()
            mood_rating = request.data.get('mood_rating', None)
            tags_list = parse_tags(request.data.get('tags', None))
            entry_id = request.data.get('entry_id', None)

            # Content is required for saving
            if not content:
                return Response({
                    'status': 'error',
                    'message': 'Obsah nemůže být prázdný'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate mood_rating if provided
            if mood_rating is not None:
                try:
                    mood_rating = int(mood_rating)
                    if not (1 <= mood_rating <= 5):
                        return Response({
                            'status': 'error',
                            'message': 'Hodnocení nálady musí být mezi 1 a 5'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except (TypeError, ValueError):
                    return Response({
                        'status': 'error',
                        'message': 'Neplatné hodnocení nálady'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Atomic transaction to prevent data loss from concurrent updates
            with transaction.atomic():
                if entry_id:
                    # Update existing entry
                    try:
                        # Lock row for update to prevent race conditions
                        entry = Entry.objects.select_for_update().get(
                            id=entry_id,
                            user=request.user
                        )

                        # Check if entry is from today - prevent editing past entries
                        entry_date = get_user_local_date(entry.created_at, request.user.timezone)
                        today_date = get_user_local_date(timezone.now(), request.user.timezone)

                        if entry_date != today_date:
                            return Response({
                                'status': 'error',
                                'message': 'Cannot edit past entries'
                            }, status=status.HTTP_403_FORBIDDEN)
                        entry.title = title
                        entry.set_content(content)
                        entry.mood_rating = mood_rating
                        entry.save()

                        # Update tags
                        if tags_list is not None:
                            entry.tags.set(tags_list)

                        return Response({
                            'status': 'success',
                            'message': 'Uloženo',
                            'entry_id': str(entry.id),
                            'is_new': False
                        })
                    except Entry.DoesNotExist:
                        return Response({
                            'status': 'error',
                            'message': 'Záznam nenalezen'
                        }, status=status.HTTP_404_NOT_FOUND)
                else:
                    # Create new entry with encrypted content
                    entry = Entry(
                        user=request.user,
                        title=title,
                        mood_rating=mood_rating
                    )
                    entry.set_content(content)
                    entry.save()

                    # Add tags if provided
                    if tags_list is not None:
                        entry.tags.set(tags_list)

                    return Response({
                        'status': 'success',
                        'message': 'Uloženo',
                        'entry_id': str(entry.id),
                        'is_new': True
                    }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Log the full exception with stack trace on the server
            logger.exception('Unexpected error during auto-save')

            # Return generic error message to the client
            return Response({
                'status': 'error',
                'message': 'Chyba při ukládání.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """
    Health check endpoint - returns 200 if healthy, 503 if unhealthy.

    This endpoint is unauthenticated and used by:
    - Docker health checks
    - Load balancers
    - Uptime monitoring services (UptimeRobot, etc.)
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def get(self, request):
        """Check application health."""
        import time
        components = {}
        timings = {}
        is_healthy = True

        # Check 1: Database connectivity
        start = time.time()
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            components['database'] = 'healthy'
        except Exception as e:
            logger.error(f"Health check - Database unhealthy: {str(e)}", exc_info=True)
            components['database'] = 'unhealthy'
            is_healthy = False
        timings['database_ms'] = int((time.time() - start) * 1000)

        # Check 2: Redis cache connectivity (degraded if unavailable, not critical)
        start = time.time()
        try:
            cache.set('health_check', 'ok', timeout=10)
            if cache.get('health_check') == 'ok':
                components['redis'] = 'healthy'
            else:
                logger.warning("Health check - Redis degraded: cache read failed")
                components['redis'] = 'degraded'
        except Exception as e:
            logger.warning(f"Health check - Redis degraded: {str(e)}")
            components['redis'] = 'degraded'
        timings['redis_ms'] = int((time.time() - start) * 1000)

        # Check 3: Celery - skip entirely for health checks (not critical)
        # The inspect.active() call is slow and Celery is optional
        components['celery'] = 'skipped'

        response_data = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'components': components,
            'timings': timings,
        }

        response_status = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(response_data, status=response_status)
