"""
API views for QuietPage.

This module contains ViewSets and API views for handling REST requests
for journal entries, dashboard data, and autosave functionality.
"""

import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from django.db.models import Sum
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone

from apps.journal.models import Entry
from apps.journal.utils import get_random_quote
from apps.api.serializers import (
    EntrySerializer,
    EntryListSerializer,
    DashboardStatsSerializer,
)

logger = logging.getLogger(__name__)


# Inspirational quotes for dashboard
QUOTES = [
    {"text": "Psaní je snadné. Stačí sednout a otevřít žílu.", "author": "Red Smith"},
    {"text": "Neexistuje nic takového jako dobré psaní, pouze dobré přepisování.", "author": "Robert Graves"},
    {"text": "První drafty jsou vždy špatné. První verze čehokoliv jsou špatné.", "author": "Ernest Hemingway"},
    {"text": "Chceš-li být spisovatelem, musíš dělat dvě věci: hodně číst a hodně psát.", "author": "Stephen King"},
    {"text": "Nejlepší čas na psaní je teď.", "author": "Anaïs Nin"},
    {"text": "Píšu, abych zjistil, co si myslím.", "author": "Joan Didion"},
    {"text": "Začni psát, bez ohledu na to, co. Voda neteče, dokud neotočíš kohoutek.", "author": "Louis L'Amour"},
    {"text": "Psaní je prozkoumávání. Začínáš od ničeho a učíš se cestou.", "author": "E.L. Doctorow"},
    {"text": "Nemusíš být skvělý, abys mohl začít, ale musíš začít, abys mohl být skvělý.", "author": "Zig Ziglar"},
    {"text": "Tvoje myšlenky si zaslouží být vyslyšeny, i kdyby to bylo jen tebou samotným.", "author": None},
]


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
        ).only(
            'id', 'title', 'created_at', 'mood_rating', 'word_count'
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

            today_words = Entry.objects.filter(
                user=user,
                created_at__gte=today_start,
                created_at__lte=today_end
            ).aggregate(
                total=Sum('word_count')
            )['total'] or 0

            stats = {
                'today_words': today_words,
                'daily_goal': user.daily_word_goal,
                'total_entries': Entry.objects.filter(user=user).count(),
                'current_streak': user.current_streak,
                'longest_streak': user.longest_streak,
                'total_words': Entry.objects.filter(user=user).aggregate(
                    total=Sum('word_count')
                )['total'] or 0,
            }
            cache.set(cache_key, stats, 300)  # Cache for 5 minutes

        # Random inspirational quote
        quote = get_random_quote()

        return Response({
            'greeting': greeting,
            'stats': stats,
            'recent_entries': EntryListSerializer(
                recent_entries,
                many=True,
                context={'request': request}
            ).data,
            'quote': quote,
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

    def get_today_date_range(self, user):
        """Vrátí start/end datetime pro dnešek v user timezone."""
        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return today_start, today_end

    def get(self, request):
        """Vrátí dnešní záznam pokud existuje, jinak 404."""
        user = request.user
        today_start, today_end = self.get_today_date_range(user)

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

        today_start, today_end = self.get_today_date_range(user)

        with transaction.atomic():
            entry = Entry.objects.filter(
                user=user,
                created_at__gte=today_start,
                created_at__lte=today_end
            ).select_for_update().first()

            if entry:
                # Update existujícího záznamu
                entry.title = (request.data.get('title') or '').strip()
                entry.content = content
                entry.mood_rating = request.data.get('mood_rating', None)
                entry.save()

                # Update tagů
                tags_data = request.data.get('tags', None)
                if tags_data is not None:
                    if isinstance(tags_data, str):
                        tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()]
                    elif isinstance(tags_data, list):
                        tags_list = [str(tag).strip() for tag in tags_data if str(tag).strip()]
                    else:
                        tags_list = []
                    entry.tags.set(tags_list)

                serializer = EntrySerializer(entry, context={'request': request})
                return Response(serializer.data)
            else:
                # Vytvoření nového záznamu (streak signal se spustí)
                entry = Entry.objects.create(
                    user=user,
                    title=(request.data.get('title') or '').strip(),
                    content=content,
                    mood_rating=request.data.get('mood_rating', None)
                )

                # Přidání tagů
                tags_data = request.data.get('tags', None)
                if tags_data:
                    if isinstance(tags_data, str):
                        tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()]
                    elif isinstance(tags_data, list):
                        tags_list = [str(tag).strip() for tag in tags_data if str(tag).strip()]
                    else:
                        tags_list = []
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
            tags_data = request.data.get('tags', None)
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

            # Process tags - handle both comma-separated string and list
            tags_list = []
            if tags_data:
                if isinstance(tags_data, str):
                    tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()]
                elif isinstance(tags_data, list):
                    tags_list = [str(tag).strip() for tag in tags_data if str(tag).strip()]

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
                        entry.title = title
                        entry.content = content
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
                    # Create new entry
                    entry = Entry.objects.create(
                        user=request.user,
                        title=title,
                        content=content,
                        mood_rating=mood_rating
                    )

                    # Add tags if provided
                    if tags_list:
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

    def get(self, request):
        """Check application health."""
        components = {}
        is_healthy = True

        # Check 1: Database connectivity
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            components['database'] = 'healthy'
        except Exception as e:
            components['database'] = f'unhealthy: {str(e)}'
            is_healthy = False

        # Check 2: Redis cache connectivity
        try:
            cache.set('health_check', 'ok', timeout=10)
            if cache.get('health_check') == 'ok':
                components['redis'] = 'healthy'
            else:
                components['redis'] = 'unhealthy: cache read failed'
                is_healthy = False
        except Exception as e:
            components['redis'] = f'unhealthy: {str(e)}'
            is_healthy = False

        # Check 3: Celery worker availability (basic check)
        try:
            from config.celery import app as celery_app
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()

            if active_workers and len(active_workers) > 0:
                components['celery'] = 'healthy'
            else:
                components['celery'] = 'unhealthy: no active workers'
        except Exception as e:
            components['celery'] = f'degraded: {str(e)}'

        response_data = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'components': components,
        }

        response_status = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(response_data, status=response_status)
