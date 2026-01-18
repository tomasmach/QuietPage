# Dashboard Redesign - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the dashboard from a passive page into an inspirational hub with writing prompts, featured historical entries, and weekly statistics.

**Architecture:** Backend adds FeaturedEntry model for cross-device consistency, extends DashboardView with weekly stats and featured entry data, adds refresh endpoint. Frontend adds three new components (WritingPrompt, FeaturedEntry, WeeklyStats) with full i18n support.

**Tech Stack:** Django REST Framework, React 19, TypeScript, Tailwind CSS, i18n via LanguageContext

---

## Task 1: Create FeaturedEntry Model

**Files:**
- Modify: `apps/journal/models.py`
- Create: `apps/journal/migrations/XXXX_featuredentry.py` (auto-generated)

**Step 1: Add FeaturedEntry model to models.py**

Add after the `Entry` class (around line 125):

```python
class FeaturedEntry(models.Model):
    """
    Stores the randomly selected 'memory' entry shown on dashboard each day.

    Ensures same entry is shown across all devices for the same user on the same day.
    Date is stored in user's timezone to handle midnight correctly.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='featured_entries'
    )
    date = models.DateField(
        help_text="Date in user's timezone when this entry was featured"
    )
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name='featured_appearances'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Featured Entry"
        verbose_name_plural = "Featured Entries"
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.entry_id}"
```

**Step 2: Generate migration**

Run: `uv run python manage.py makemigrations journal --name featuredentry`

Expected: Migration file created in `apps/journal/migrations/`

**Step 3: Apply migration**

Run: `uv run python manage.py migrate`

Expected: `Applying journal.XXXX_featuredentry... OK`

**Step 4: Commit**

```bash
git add apps/journal/models.py apps/journal/migrations/
git commit -m "feat: add FeaturedEntry model for dashboard memories"
```

---

## Task 2: Write Tests for FeaturedEntry Selection Logic

**Files:**
- Create: `apps/api/tests/test_dashboard_featured.py`

**Step 1: Create test file with all test cases**

```python
"""
Tests for FeaturedEntry selection and refresh logic in DashboardView.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from zoneinfo import ZoneInfo
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory
from apps.journal.models import FeaturedEntry


@pytest.mark.django_db
class TestFeaturedEntrySelection:
    """Tests for featured entry selection on dashboard."""

    def test_featured_entry_not_shown_with_less_than_10_entries(self):
        """Featured entry should be null when user has < 10 entries."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create only 5 entries
        EntryFactory.create_batch(5, user=user)

        response = client.get('/api/v1/dashboard/')

        assert response.status_code == 200
        assert response.data['featured_entry'] is None

    def test_featured_entry_shown_with_10_or_more_entries(self):
        """Featured entry should be returned when user has >= 10 entries."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create 10 entries with dates in the past
        for i in range(10):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i+1)
            )

        response = client.get('/api/v1/dashboard/')

        assert response.status_code == 200
        assert response.data['featured_entry'] is not None
        assert 'id' in response.data['featured_entry']
        assert 'content_preview' in response.data['featured_entry']
        assert 'days_ago' in response.data['featured_entry']

    def test_featured_entry_consistent_across_requests(self):
        """Same featured entry should be returned on multiple requests same day."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create 15 entries
        for i in range(15):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i+1)
            )

        response1 = client.get('/api/v1/dashboard/')
        response2 = client.get('/api/v1/dashboard/')

        assert response1.data['featured_entry']['id'] == response2.data['featured_entry']['id']

    def test_featured_entry_stored_in_database(self):
        """Featured entry selection should be persisted in FeaturedEntry model."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create 10 entries
        for i in range(10):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i+1)
            )

        assert FeaturedEntry.objects.filter(user=user).count() == 0

        client.get('/api/v1/dashboard/')

        assert FeaturedEntry.objects.filter(user=user).count() == 1

    def test_featured_entry_excludes_today(self):
        """Featured entry should never be from today."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create 9 past entries + 1 today
        for i in range(9):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i+1)
            )
        today_entry = EntryFactory(user=user)  # Today's entry

        response = client.get('/api/v1/dashboard/')

        # Should have featured entry (10 total entries)
        assert response.data['featured_entry'] is not None
        # Should not be today's entry
        assert response.data['featured_entry']['id'] != str(today_entry.id)


@pytest.mark.django_db
class TestFeaturedEntryRefresh:
    """Tests for featured entry refresh endpoint."""

    def test_refresh_returns_different_entry(self):
        """Refresh should return a different entry than current."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create 15 entries (need enough for refresh to find different one)
        for i in range(15):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i+1)
            )

        # Get initial featured entry
        response1 = client.get('/api/v1/dashboard/')
        initial_id = response1.data['featured_entry']['id']

        # Refresh
        response2 = client.post('/api/v1/dashboard/refresh-featured/')

        assert response2.status_code == 200
        assert response2.data['featured_entry']['id'] != initial_id

    def test_refresh_updates_database(self):
        """Refresh should update the FeaturedEntry in database."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        for i in range(15):
            EntryFactory(
                user=user,
                created_at=timezone.now() - timedelta(days=i+1)
            )

        # Trigger initial selection
        client.get('/api/v1/dashboard/')
        initial_featured = FeaturedEntry.objects.get(user=user)
        initial_entry_id = initial_featured.entry_id

        # Refresh
        client.post('/api/v1/dashboard/refresh-featured/')

        updated_featured = FeaturedEntry.objects.get(user=user)
        assert updated_featured.entry_id != initial_entry_id

    def test_refresh_with_only_one_valid_entry_returns_same(self):
        """When only one valid entry exists, refresh returns same entry."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create 9 entries today (excluded) and 1 yesterday
        for i in range(9):
            EntryFactory(user=user)  # Today
        EntryFactory(
            user=user,
            created_at=timezone.now() - timedelta(days=1)
        )

        response1 = client.get('/api/v1/dashboard/')
        response2 = client.post('/api/v1/dashboard/refresh-featured/')

        # Should return same entry (only one valid option)
        assert response1.data['featured_entry']['id'] == response2.data['featured_entry']['id']

    def test_refresh_requires_authentication(self):
        """Refresh endpoint should require authentication."""
        client = APIClient()

        response = client.post('/api/v1/dashboard/refresh-featured/')

        assert response.status_code == 401


@pytest.mark.django_db
class TestWeeklyStats:
    """Tests for weekly statistics in dashboard response."""

    def test_weekly_stats_included_in_response(self):
        """Dashboard should include weekly_stats object."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/v1/dashboard/')

        assert response.status_code == 200
        assert 'weekly_stats' in response.data
        assert 'total_words' in response.data['weekly_stats']
        assert 'best_day' in response.data['weekly_stats']

    def test_weekly_stats_calculates_last_7_days(self):
        """Weekly stats should sum words from last 7 days only."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create entry 3 days ago with 500 words
        entry1 = EntryFactory(
            user=user,
            content=' '.join(['word'] * 500),
            created_at=timezone.now() - timedelta(days=3)
        )

        # Create entry 10 days ago with 1000 words (should be excluded)
        EntryFactory(
            user=user,
            content=' '.join(['word'] * 1000),
            created_at=timezone.now() - timedelta(days=10)
        )

        response = client.get('/api/v1/dashboard/')

        # Should only count the 500 words from last 7 days
        assert response.data['weekly_stats']['total_words'] == 500

    def test_weekly_stats_best_day_format(self):
        """Best day should include date, words, and weekday."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Create entry 2 days ago
        EntryFactory(
            user=user,
            content=' '.join(['word'] * 800),
            created_at=timezone.now() - timedelta(days=2)
        )

        response = client.get('/api/v1/dashboard/')

        best_day = response.data['weekly_stats']['best_day']
        assert best_day is not None
        assert 'date' in best_day
        assert 'words' in best_day
        assert 'weekday' in best_day
        assert best_day['words'] == 800

    def test_weekly_stats_no_entries(self):
        """Weekly stats should handle zero entries gracefully."""
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/v1/dashboard/')

        assert response.data['weekly_stats']['total_words'] == 0
        assert response.data['weekly_stats']['best_day'] is None
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest apps/api/tests/test_dashboard_featured.py -v`

Expected: All tests FAIL (endpoints/logic not implemented yet)

**Step 3: Commit test file**

```bash
git add apps/api/tests/test_dashboard_featured.py
git commit -m "test: add tests for dashboard featured entry and weekly stats"
```

---

## Task 3: Implement FeaturedEntry Logic in DashboardView

**Files:**
- Modify: `apps/api/views.py`

**Step 1: Add imports at top of file**

Add to existing imports (around line 12):

```python
from datetime import timedelta
```

Add to model imports (around line 23):

```python
from apps.journal.models import Entry, FeaturedEntry
```

**Step 2: Add helper methods to DashboardView class**

Add these methods inside `DashboardView` class (after `get_greeting` method, around line 133):

```python
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
        # Check minimum entries requirement
        entry_count = Entry.objects.filter(user=user).count()
        if entry_count < 10:
            return None

        # Try to get existing featured entry for today
        featured = FeaturedEntry.objects.filter(
            user=user,
            date=user_date
        ).select_related('entry').first()

        if featured:
            return featured.entry

        # Get user's timezone for date comparison
        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Select random entry (exclude today's)
        random_entry = Entry.objects.filter(
            user=user
        ).exclude(
            created_at__gte=today_start
        ).order_by('?').first()

        if not random_entry:
            return None

        # Save for consistency across devices
        FeaturedEntry.objects.create(
            user=user,
            date=user_date,
            entry=random_entry
        )

        return random_entry

    def get_weekly_stats(self, user):
        """
        Calculate statistics for the last 7 days.

        Returns dict with total_words and best_day info.
        """
        user_tz = ZoneInfo(str(user.timezone))
        now = timezone.now().astimezone(user_tz)

        # Calculate 7 days ago (start of that day)
        week_ago = (now - timedelta(days=7)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Get entries from last 7 days
        weekly_entries = Entry.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).values('created_at', 'word_count')

        total_words = 0
        daily_words = {}

        for entry in weekly_entries:
            total_words += entry['word_count']
            # Group by date in user's timezone
            entry_date = entry['created_at'].astimezone(user_tz).date()
            daily_words[entry_date] = daily_words.get(entry_date, 0) + entry['word_count']

        # Find best day
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

        # Calculate days ago
        entry_date = entry.created_at.date()
        days_ago = (user_date - entry_date).days

        # Content preview (first 200 chars)
        content_preview = entry.content[:200] if entry.content else ''
        if len(entry.content) > 200:
            content_preview += '...'

        return {
            'id': str(entry.id),
            'title': entry.title,
            'content_preview': content_preview,
            'created_at': entry.created_at.isoformat(),
            'word_count': entry.word_count,
            'days_ago': days_ago
        }
```

**Step 3: Update the get method to include new data**

Replace the existing `get` method (around line 134) with:

```python
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
```

**Step 4: Run tests**

Run: `uv run pytest apps/api/tests/test_dashboard_featured.py::TestFeaturedEntrySelection -v`

Expected: Selection tests PASS

Run: `uv run pytest apps/api/tests/test_dashboard_featured.py::TestWeeklyStats -v`

Expected: Weekly stats tests PASS

**Step 5: Commit**

```bash
git add apps/api/views.py
git commit -m "feat: add featured entry and weekly stats to dashboard"
```

---

## Task 4: Implement RefreshFeaturedEntry Endpoint

**Files:**
- Modify: `apps/api/views.py`
- Modify: `apps/api/urls.py`

**Step 1: Add RefreshFeaturedEntryView class to views.py**

Add after `DashboardView` class (around line 250):

```python
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

        # Check minimum entries
        entry_count = Entry.objects.filter(user=user).count()
        if entry_count < 10:
            return Response({
                'featured_entry': None,
                'message': 'Not enough entries for featured entry'
            })

        # Get current featured to exclude it
        current = FeaturedEntry.objects.filter(user=user, date=user_date).first()
        exclude_ids = [current.entry_id] if current else []

        # Delete current
        FeaturedEntry.objects.filter(user=user, date=user_date).delete()

        # Get today's start for exclusion
        now = timezone.now().astimezone(user_tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Select new random (excluding current and today's entries)
        new_entry = Entry.objects.filter(
            user=user
        ).exclude(
            id__in=exclude_ids
        ).exclude(
            created_at__gte=today_start
        ).order_by('?').first()

        # If no other entry available, use the excluded one
        if not new_entry and exclude_ids:
            new_entry = Entry.objects.get(id=exclude_ids[0])

        if new_entry:
            # Save new
            FeaturedEntry.objects.create(
                user=user,
                date=user_date,
                entry=new_entry
            )

        # Serialize response
        featured_data = None
        if new_entry:
            days_ago = (user_date - new_entry.created_at.date()).days
            content_preview = new_entry.content[:200] if new_entry.content else ''
            if len(new_entry.content) > 200:
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
```

**Step 2: Add URL route**

In `apps/api/urls.py`, add import (around line 22):

```python
from apps.api.views import (
    EntryViewSet,
    DashboardView,
    AutosaveView,
    TodayEntryView,
    RefreshFeaturedEntryView,
)
```

Add URL pattern after dashboard path (around line 54):

```python
    # Dashboard endpoints
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/refresh-featured/', RefreshFeaturedEntryView.as_view(), name='dashboard-refresh-featured'),
```

**Step 3: Run refresh tests**

Run: `uv run pytest apps/api/tests/test_dashboard_featured.py::TestFeaturedEntryRefresh -v`

Expected: All refresh tests PASS

**Step 4: Run all dashboard tests**

Run: `uv run pytest apps/api/tests/test_dashboard_featured.py -v`

Expected: All tests PASS

**Step 5: Commit**

```bash
git add apps/api/views.py apps/api/urls.py
git commit -m "feat: add refresh-featured endpoint for dashboard"
```

---

## Task 5: Add i18n Translations - Translations Interface Update

**Files:**
- Modify: `frontend/src/locales/cs.ts`

**Step 1: Update Translations interface**

Add to the `dashboard` section of the interface (around line 102-115):

```typescript
  dashboard: {
    greeting: {
      morning: string;
      afternoon: string;
      evening: string;
    };
    todayWords: string;
    newEntry: string;
    noEntries: string;
    recentEntries: string;
    viewAll: string;
    longestStreak: string;
    totalEntries: string;
    // New translations
    writingPrompt: {
      title: string;
      cta: string;
    };
    featuredEntry: {
      title: string;
      daysAgo: string;
      refresh: string;
      refreshing: string;
    };
    weeklyStats: {
      streak: string;
      streakDays: string;
      thisWeek: string;
      words: string;
      bestDay: string;
    };
    prompts: string[];
  };
```

**Step 2: Add Czech translations**

Update the `cs` object's dashboard section (around line 506-519):

```typescript
  dashboard: {
    greeting: {
      morning: 'Dobr\u00e9 r\u00e1no',
      afternoon: 'Dobr\u00e9 odpoledne',
      evening: 'Dobr\u00fd ve\u010der',
    },
    todayWords: 'Slov dnes',
    newEntry: 'Nov\u00fd z\u00e1znam',
    noEntries: 'Zat\u00edm \u017e\u00e1dn\u00e9 z\u00e1znamy. Za\u010dni ps\u00e1t!',
    recentEntries: 'Ned\u00e1vn\u00e9 z\u00e1znamy',
    viewAll: 'Zobrazit v\u0161e',
    longestStreak: 'Nejdel\u0161\u00ed',
    totalEntries: 'Celkem z\u00e1znam\u016f',
    writingPrompt: {
      title: 'Dne\u0161n\u00ed inspirace',
      cta: 'Za\u010d\u00edt ps\u00e1t',
    },
    featuredEntry: {
      title: 'Z tv\u00e9 historie',
      daysAgo: 'p\u0159ed {{count}} dny',
      refresh: 'Zobrazit jin\u00fd',
      refreshing: 'Na\u010d\u00edt\u00e1m...',
    },
    weeklyStats: {
      streak: 'S\u00e9rie',
      streakDays: '{{count}} dn\u00ed',
      thisWeek: 'Tento t\u00fdden',
      words: '{{count}} slov',
      bestDay: 'Nejlep\u0161\u00ed den',
    },
    prompts: [
      'Co t\u011b dnes p\u0159ekvapilo?',
      'Popi\u0161 moment, kdy ses dnes c\u00edtil/a \u017eiv\u011b.',
      'Kdybys mohl/a zm\u011bnit jednu v\u011bc na dne\u0161ku, co by to bylo?',
      'Za co jsi dnes vd\u011b\u010dn\u00fd/\u00e1?',
      'Co t\u011b dnes rozesm\u00e1lo?',
      'Jak\u00e1 my\u0161lenka se ti dnes po\u0159\u00e1d vrac\u00ed?',
      'Co nov\u00e9ho ses dnes nau\u010dil/a?',
      'Kdo ti dnes ud\u011blal radost a pro\u010d?',
      'Jak\u00fd byl nejt\u011b\u017e\u0161\u00ed moment dne?',
      'Co bys d\u011blal/a, kdybys v\u011bd\u011bl/a, \u017ee nem\u016f\u017ee\u0161 selhat?',
      'Popi\u0161 sv\u016fj ide\u00e1ln\u00ed den.',
      'Na co se te\u0161\u00ed\u0161 z\u00edtra?',
      'Co t\u011b v posledn\u00ed dob\u011b tr\u00e1p\u00ed?',
      'Jak\u00fd je tv\u016fj nejv\u011bt\u0161\u00ed sen?',
      'Co by sis \u0159ekl/a sv\u00e9mu mladšímu já?',
      'Popi\u0161 m\u00edsto, kde se c\u00edt\u00ed\u0161 v bezpe\u010d\u00ed.',
      'Co t\u011b nab\u00edj\u00ed energi\u00ed?',
      'Jak\u00e9 mal\u00e9 radosti si u\u017e\u00edv\u00e1\u0161?',
      'Co bys cht\u011bl/a zm\u011bnit na sv\u00e9m \u017eivot\u011b?',
      'Popi\u0161 \u010dlov\u011bka, kter\u00e9ho obdivuje\u0161.',
      'Jak\u00fd je tv\u016fj obl\u00edben\u00fd zp\u016fsob relaxace?',
      'Co t\u011b d\u011bl\u00e1 \u0161\u0165astn\u00fdm/ou?',
      'Jak\u00fd byl tv\u016fj nejlep\u0161\u00ed z\u00e1\u017eitek tohoto roku?',
      'Na co jsi hrd\u00fd/\u00e1?',
      'Co t\u011b posledn\u011b inspirovalo?',
      'Jak\u00e9 jsou tv\u00e9 priority v \u017eivot\u011b?',
      'Popi\u0161, jak se pr\u00e1v\u011b te\u010f c\u00edt\u00ed\u0161.',
      'Co by ses cht\u011bl/a nau\u010dit?',
      'Jak\u00fd je tv\u016fj vztah k \u010dasu?',
      'Co t\u011b v posledn\u00ed dob\u011b posunulo vp\u0159ed?',
      'Popi\u0161 sv\u016fj nejlep\u0161\u00ed p\u0159\u00e1telsk\u00fd vztah.',
      'Co d\u011bl\u00e1\u0161 pro sv\u00e9 zdrav\u00ed?',
      'Jak vypad\u00e1 tv\u016fj ide\u00e1ln\u00ed v\u00edkend?',
      'Co t\u011b motivuje vstávat ráno?',
      'Jak\u00fd je tv\u016fj nejv\u011bt\u0161\u00ed strach?',
      'Co bys d\u011blal/a, kdybys m\u011bl/a neomezen\u00e9 prost\u0159edky?',
      'Popi\u0161 sv\u016fj obl\u00edben\u00fd ro\u010dn\u00ed obdob\u00ed.',
      'Co t\u011b na sob\u011b p\u0159ekvapuje?',
      'Jak\u00e9 knihy t\u011b ovlivnily?',
      'Co znamen\u00e1 pro tebe \u00fasp\u011bch?',
      'Popi\u0161 m\u00edsto, kam by ses cht\u011bl/a pod\u00edvat.',
      'Co d\u011bl\u00e1\u0161, kdy\u017e pot\u0159ebuje\u0161 uklidnit mysl?',
      'Jak\u00e9 jsou tv\u00e9 hodnoty?',
      'Co t\u011b posledn\u011b p\u0159inutilo zamyslet se?',
      'Popi\u0161 sv\u016fj vztah k p\u0159\u00edrod\u011b.',
      'Co bys poradil/a n\u011bkomu, kdo za\u010d\u00edn\u00e1 ps\u00e1t den\u00edk?',
      'Jak se stav\u00ed\u0161 k chyb\u00e1m?',
      'Co t\u011b d\u011bl\u00e1 jedine\u010dn\u00fdm/ou?',
      'Jak\u00fd je tv\u016fj obl\u00edben\u00fd zp\u016fsob tr\u00e1ven\u00ed voln\u00e9ho \u010dasu?',
      'Na co se t\u011b\u0161\u00ed\u0161 v budoucnosti?',
    ],
  },
```

**Step 3: Commit**

```bash
git add frontend/src/locales/cs.ts
git commit -m "feat: add Czech translations for dashboard redesign"
```

---

## Task 6: Add English Translations

**Files:**
- Modify: `frontend/src/locales/en.ts`

**Step 1: Update English translations**

Update the `en` object's dashboard section (around line 104-117):

```typescript
  dashboard: {
    greeting: {
      morning: 'Good morning',
      afternoon: 'Good afternoon',
      evening: 'Good evening',
    },
    todayWords: 'Words today',
    newEntry: 'New entry',
    noEntries: 'No entries yet. Start writing!',
    recentEntries: 'Recent entries',
    viewAll: 'View all',
    longestStreak: 'Longest',
    totalEntries: 'Total entries',
    writingPrompt: {
      title: "Today's inspiration",
      cta: 'Start writing',
    },
    featuredEntry: {
      title: 'From your history',
      daysAgo: '{{count}} days ago',
      refresh: 'Show another',
      refreshing: 'Loading...',
    },
    weeklyStats: {
      streak: 'Streak',
      streakDays: '{{count}} days',
      thisWeek: 'This week',
      words: '{{count}} words',
      bestDay: 'Best day',
    },
    prompts: [
      'What surprised you today?',
      'Describe a moment when you felt truly alive today.',
      'If you could change one thing about today, what would it be?',
      'What are you grateful for today?',
      'What made you laugh today?',
      'What thought keeps coming back to you today?',
      'What new thing did you learn today?',
      'Who made you happy today and why?',
      'What was the hardest moment of the day?',
      'What would you do if you knew you couldn\'t fail?',
      'Describe your ideal day.',
      'What are you looking forward to tomorrow?',
      'What has been troubling you lately?',
      'What is your biggest dream?',
      'What would you tell your younger self?',
      'Describe a place where you feel safe.',
      'What energizes you?',
      'What small joys do you enjoy?',
      'What would you like to change in your life?',
      'Describe a person you admire.',
      'What is your favorite way to relax?',
      'What makes you happy?',
      'What was your best experience this year?',
      'What are you proud of?',
      'What inspired you recently?',
      'What are your priorities in life?',
      'Describe how you\'re feeling right now.',
      'What would you like to learn?',
      'What is your relationship with time?',
      'What has pushed you forward recently?',
      'Describe your best friendship.',
      'What do you do for your health?',
      'What does your ideal weekend look like?',
      'What motivates you to get up in the morning?',
      'What is your biggest fear?',
      'What would you do with unlimited resources?',
      'Describe your favorite season.',
      'What surprises you about yourself?',
      'What books have influenced you?',
      'What does success mean to you?',
      'Describe a place you\'d like to visit.',
      'What do you do when you need to calm your mind?',
      'What are your values?',
      'What made you think recently?',
      'Describe your relationship with nature.',
      'What advice would you give someone starting a journal?',
      'How do you deal with mistakes?',
      'What makes you unique?',
      'What is your favorite way to spend free time?',
      'What are you looking forward to in the future?',
    ],
  },
```

**Step 2: Commit**

```bash
git add frontend/src/locales/en.ts
git commit -m "feat: add English translations for dashboard redesign"
```

---

## Task 7: Update useDashboard Hook

**Files:**
- Modify: `frontend/src/hooks/useDashboard.ts`

**Step 1: Update interfaces**

Replace the entire file content:

```typescript
import { useEffect, useState, useCallback } from 'react';
import { api } from '../lib/api';

export interface DashboardStats {
  todayWords: number;
  dailyGoal: number;
  currentStreak: number;
  longestStreak: number;
  totalEntries: number;
}

export interface RecentEntry {
  id: string;
  title: string;
  content_preview: string;
  created_at: string;
  mood_rating: number | null;
  word_count: number;
}

export interface Quote {
  text: string;
  author: string;
}

export interface FeaturedEntry {
  id: string;
  title: string;
  content_preview: string;
  created_at: string;
  word_count: number;
  days_ago: number;
}

export interface WeeklyStats {
  totalWords: number;
  bestDay: {
    date: string;
    words: number;
    weekday: string;
  } | null;
}

export interface DashboardData {
  greeting: string;
  stats: DashboardStats;
  recentEntries: RecentEntry[];
  quote: Quote | null;
  hasEntries: boolean;
  featuredEntry: FeaturedEntry | null;
  weeklyStats: WeeklyStats;
}

// API response with snake_case from backend
interface DashboardStatsAPI {
  today_words: number;
  daily_goal: number;
  current_streak: number;
  longest_streak: number;
  total_entries: number;
}

interface FeaturedEntryAPI {
  id: string;
  title: string;
  content_preview: string;
  created_at: string;
  word_count: number;
  days_ago: number;
}

interface WeeklyStatsAPI {
  total_words: number;
  best_day: {
    date: string;
    words: number;
    weekday: string;
  } | null;
}

interface DashboardDataAPI {
  greeting: string;
  stats: DashboardStatsAPI;
  recent_entries: RecentEntry[];
  quote: Quote | null;
  featured_entry: FeaturedEntryAPI | null;
  weekly_stats: WeeklyStatsAPI;
}

interface UseDashboardReturn {
  data: DashboardData | null;
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
  refreshFeaturedEntry: () => Promise<void>;
  isRefreshingFeatured: boolean;
}

/**
 * Hook for fetching dashboard data
 * Fetches from /api/v1/dashboard/
 */
export function useDashboard(): UseDashboardReturn {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isRefreshingFeatured, setIsRefreshingFeatured] = useState(false);

  const fetchDashboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get<DashboardDataAPI>('/dashboard/');

      // Convert snake_case from backend to camelCase for frontend
      const dashboardData: DashboardData = {
        greeting: response.greeting,
        stats: {
          todayWords: response.stats.today_words ?? 0,
          dailyGoal: response.stats.daily_goal ?? 750,
          currentStreak: response.stats.current_streak ?? 0,
          longestStreak: response.stats.longest_streak ?? 0,
          totalEntries: response.stats.total_entries ?? 0,
        },
        recentEntries: response.recent_entries || [],
        quote: response.quote,
        hasEntries: (response.recent_entries || []).length > 0,
        featuredEntry: response.featured_entry,
        weeklyStats: {
          totalWords: response.weekly_stats?.total_words ?? 0,
          bestDay: response.weekly_stats?.best_day ?? null,
        },
      };

      setData(dashboardData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch dashboard'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshFeaturedEntry = useCallback(async () => {
    if (!data) return;

    setIsRefreshingFeatured(true);

    try {
      const response = await api.post<{ featured_entry: FeaturedEntryAPI | null }>(
        '/dashboard/refresh-featured/'
      );

      setData(prev => prev ? {
        ...prev,
        featuredEntry: response.featured_entry,
      } : null);
    } catch (err) {
      console.error('Failed to refresh featured entry:', err);
    } finally {
      setIsRefreshingFeatured(false);
    }
  }, [data]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return {
    data,
    isLoading,
    error,
    refresh: fetchDashboard,
    refreshFeaturedEntry,
    isRefreshingFeatured,
  };
}
```

**Step 2: Commit**

```bash
git add frontend/src/hooks/useDashboard.ts
git commit -m "feat: extend useDashboard hook with featured entry and weekly stats"
```

---

## Task 8: Create WritingPrompt Component

**Files:**
- Create: `frontend/src/components/dashboard/WritingPrompt.tsx`

**Step 1: Create component file**

```typescript
import { Lightbulb } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import { cn } from '../../lib/utils';

/**
 * Get the day of year (1-366)
 */
function getDayOfYear(date: Date): number {
  const start = new Date(date.getFullYear(), 0, 0);
  const diff = date.getTime() - start.getTime();
  const oneDay = 1000 * 60 * 60 * 24;
  return Math.floor(diff / oneDay);
}

/**
 * Daily writing prompt component
 * Shows a rotating prompt based on day of year
 */
export function WritingPrompt() {
  const navigate = useNavigate();
  const { t, translations } = useLanguage();

  // Get prompt for today
  const prompts = translations.dashboard.prompts;
  const dayOfYear = getDayOfYear(new Date());
  const promptIndex = dayOfYear % prompts.length;
  const todayPrompt = prompts[promptIndex];

  const handleStartWriting = () => {
    navigate('/write');
  };

  return (
    <div className={cn(
      "border-2 border-border bg-bg-panel p-6 shadow-hard",
      "theme-aware"
    )}>
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb size={18} className="text-text-main" />
        <h3 className="text-sm font-bold uppercase tracking-widest text-text-main">
          {t('dashboard.writingPrompt.title')}
        </h3>
      </div>

      {/* Prompt text */}
      <p className="text-lg text-text-main leading-relaxed mb-6">
        {todayPrompt}
      </p>

      {/* CTA Button */}
      <button
        onClick={handleStartWriting}
        className={cn(
          "px-6 py-3 bg-accent text-accent-fg font-bold",
          "border-2 border-border shadow-hard",
          "hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none",
          "transition-all duration-150"
        )}
      >
        {t('dashboard.writingPrompt.cta')}
      </button>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/dashboard/WritingPrompt.tsx
git commit -m "feat: add WritingPrompt component"
```

---

## Task 9: Create FeaturedEntry Component

**Files:**
- Create: `frontend/src/components/dashboard/FeaturedEntry.tsx`

**Step 1: Create component file**

```typescript
import { History, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import { cn } from '../../lib/utils';
import type { FeaturedEntry as FeaturedEntryType } from '../../hooks/useDashboard';

interface FeaturedEntryProps {
  entry: FeaturedEntryType;
  onRefresh: () => void;
  isRefreshing: boolean;
}

/**
 * Format date for display
 */
function formatDate(dateString: string, locale: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString(locale === 'cs' ? 'cs-CZ' : 'en-US', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

/**
 * Featured entry from history component
 * Shows a random past entry with refresh capability
 */
export function FeaturedEntry({ entry, onRefresh, isRefreshing }: FeaturedEntryProps) {
  const navigate = useNavigate();
  const { t, language } = useLanguage();

  const handleClick = () => {
    navigate(`/entries/${entry.id}`);
  };

  const handleRefresh = (e: React.MouseEvent) => {
    e.stopPropagation();
    onRefresh();
  };

  const daysAgoText = t('dashboard.featuredEntry.daysAgo').replace('{{count}}', String(entry.days_ago));

  return (
    <div
      onClick={handleClick}
      className={cn(
        "border-2 border-border bg-bg-panel p-6 shadow-hard cursor-pointer",
        "hover:border-dashed transition-all duration-150",
        "theme-aware"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <History size={18} className="text-text-main" />
          <h3 className="text-sm font-bold uppercase tracking-widest text-text-main">
            {t('dashboard.featuredEntry.title')}
          </h3>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className={cn(
            "flex items-center gap-1 text-xs font-bold uppercase text-text-muted",
            "hover:text-text-main transition-colors",
            "disabled:opacity-50"
          )}
        >
          <RefreshCw
            size={14}
            className={cn(isRefreshing && "animate-spin")}
          />
          {isRefreshing
            ? t('dashboard.featuredEntry.refreshing')
            : t('dashboard.featuredEntry.refresh')
          }
        </button>
      </div>

      {/* Date and days ago */}
      <div className="text-sm text-text-muted mb-2">
        {formatDate(entry.created_at, language)} · {daysAgoText}
      </div>

      {/* Title if exists */}
      {entry.title && (
        <h4 className="text-lg font-bold text-text-main mb-2">
          {entry.title}
        </h4>
      )}

      {/* Content preview */}
      <p className="text-text-main leading-relaxed line-clamp-3">
        {entry.content_preview}
      </p>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-border border-dashed">
        <span className="text-sm text-text-muted">
          {entry.word_count} {t('meta.wordsSuffix')}
        </span>
      </div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/dashboard/FeaturedEntry.tsx
git commit -m "feat: add FeaturedEntry component"
```

---

## Task 10: Create WeeklyStats Component

**Files:**
- Create: `frontend/src/components/dashboard/WeeklyStats.tsx`

**Step 1: Create component file**

```typescript
import { Flame, FileText, Trophy } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';
import { cn } from '../../lib/utils';
import type { DashboardStats, WeeklyStats as WeeklyStatsType } from '../../hooks/useDashboard';

interface WeeklyStatsProps {
  stats: DashboardStats;
  weeklyStats: WeeklyStatsType;
}

/**
 * Get translated weekday name
 */
function getWeekdayName(weekday: string, t: (key: string) => string): string {
  const key = `statistics.dayOfWeekChart.${weekday}Abbr`;
  return t(key);
}

/**
 * Weekly statistics component for context panel
 * Shows streak, words this week, and best day
 */
export function WeeklyStats({ stats, weeklyStats }: WeeklyStatsProps) {
  const { t } = useLanguage();

  return (
    <div className="space-y-4">
      {/* Streak */}
      <div className={cn(
        "border-2 border-border p-4 bg-bg-panel shadow-hard",
        "theme-aware"
      )}>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-bold uppercase text-text-muted">
            {t('dashboard.weeklyStats.streak')}
          </span>
          <Flame size={16} className="text-text-main" />
        </div>
        <div className="text-3xl font-bold text-text-main">
          {t('dashboard.weeklyStats.streakDays').replace('{{count}}', String(stats.currentStreak))}
        </div>
      </div>

      {/* Words this week */}
      <div className={cn(
        "border-2 border-border p-4 bg-bg-panel shadow-hard",
        "theme-aware"
      )}>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-bold uppercase text-text-muted">
            {t('dashboard.weeklyStats.thisWeek')}
          </span>
          <FileText size={16} className="text-text-main" />
        </div>
        <div className="text-3xl font-bold text-text-main">
          {t('dashboard.weeklyStats.words').replace('{{count}}', weeklyStats.totalWords.toLocaleString())}
        </div>
      </div>

      {/* Best day this week */}
      <div className={cn(
        "border-2 border-border p-4 bg-bg-panel shadow-hard",
        "theme-aware"
      )}>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-bold uppercase text-text-muted">
            {t('dashboard.weeklyStats.bestDay')}
          </span>
          <Trophy size={16} className="text-text-main" />
        </div>
        {weeklyStats.bestDay ? (
          <div>
            <div className="text-3xl font-bold text-text-main">
              {weeklyStats.bestDay.words.toLocaleString()}
            </div>
            <div className="text-sm text-text-muted">
              {getWeekdayName(weeklyStats.bestDay.weekday, t)}
            </div>
          </div>
        ) : (
          <div className="text-lg text-text-muted">—</div>
        )}
      </div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/dashboard/WeeklyStats.tsx
git commit -m "feat: add WeeklyStats component"
```

---

## Task 11: Update DashboardPage Layout

**Files:**
- Modify: `frontend/src/pages/DashboardPage.tsx`

**Step 1: Replace DashboardPage content**

```typescript
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { Card } from '../components/ui/Card';
import { Spinner } from '../components/ui/Spinner';
import { WritingPrompt } from '../components/dashboard/WritingPrompt';
import { FeaturedEntry } from '../components/dashboard/FeaturedEntry';
import { WeeklyStats } from '../components/dashboard/WeeklyStats';
import { useDashboard } from '../hooks/useDashboard';
import { useLanguage } from '../contexts/LanguageContext';

export function DashboardPage() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const {
    data,
    isLoading,
    error,
    refreshFeaturedEntry,
    isRefreshingFeatured
  } = useDashboard();

  if (isLoading) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8 flex items-center justify-center min-h-[50vh]">
          <Spinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8">
          <Card>
            <p className="text-error">
              Chyba pri nacitani dashboardu: {error?.message || 'Neznama chyba'}
            </p>
          </Card>
        </div>
      </AppLayout>
    );
  }

  // Get current date info
  const today = new Date();
  const formattedDate = today.toLocaleDateString('cs-CZ', {
    day: 'numeric',
    month: 'long',
  });

  // Get time-based greeting key
  const hour = today.getHours();
  const getGreetingKey = () => {
    if (hour < 12) return 'morning';
    if (hour < 18) return 'afternoon';
    return 'evening';
  };
  const greetingKey = getGreetingKey();

  // Calculate progress percentage
  const progressPercentage = Math.min((data.stats.todayWords / data.stats.dailyGoal) * 100, 100);

  return (
    <AppLayout
      sidebar={<Sidebar />}
      contextPanel={
        <ContextPanel>
          <WeeklyStats
            stats={data.stats}
            weeklyStats={data.weeklyStats}
          />
        </ContextPanel>
      }
    >
      <div className="p-8 space-y-8 relative">
        {/* Top Thin Progress Bar */}
        <div className="absolute top-0 left-0 w-full h-1 bg-bg-panel opacity-20">
          <div
            className="h-full bg-accent transition-all duration-500"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>

        {/* Header */}
        <div className="flex justify-between items-end border-b-2 border-border pb-4 border-dashed">
          <div>
            <div className="text-sm font-bold uppercase text-text-muted mb-1">
              {t(`dashboard.greeting.${greetingKey}`)}
            </div>
            <h1 className="text-3xl font-bold uppercase text-text-main">
              {formattedDate}
            </h1>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-text-main">{data.stats.todayWords}</div>
            <div className="text-sm font-bold uppercase text-text-muted">
              {t('meta.wordsToday')}
            </div>
          </div>
        </div>

        {/* Writing Prompt */}
        <WritingPrompt />

        {/* Featured Entry (only if available) */}
        {data.featuredEntry && (
          <FeaturedEntry
            entry={data.featuredEntry}
            onRefresh={refreshFeaturedEntry}
            isRefreshing={isRefreshingFeatured}
          />
        )}
      </div>
    </AppLayout>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/pages/DashboardPage.tsx
git commit -m "feat: update DashboardPage with new layout and components"
```

---

## Task 12: Add Frontend Tests

**Files:**
- Create: `frontend/src/components/dashboard/__tests__/WritingPrompt.test.tsx`
- Create: `frontend/src/components/dashboard/__tests__/WeeklyStats.test.tsx`

**Step 1: Create WritingPrompt test**

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { WritingPrompt } from '../WritingPrompt';

// Mock useLanguage
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'dashboard.writingPrompt.title': "Today's inspiration",
        'dashboard.writingPrompt.cta': 'Start writing',
      };
      return translations[key] || key;
    },
    translations: {
      dashboard: {
        prompts: [
          'What surprised you today?',
          'Describe a moment when you felt alive.',
          'What are you grateful for?',
        ],
      },
    },
  }),
}));

describe('WritingPrompt', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('renders prompt title', () => {
    vi.setSystemTime(new Date('2024-01-15'));

    render(
      <BrowserRouter>
        <WritingPrompt />
      </BrowserRouter>
    );

    expect(screen.getByText("Today's inspiration")).toBeInTheDocument();
  });

  it('renders CTA button', () => {
    vi.setSystemTime(new Date('2024-01-15'));

    render(
      <BrowserRouter>
        <WritingPrompt />
      </BrowserRouter>
    );

    expect(screen.getByText('Start writing')).toBeInTheDocument();
  });

  it('renders a prompt from the list', () => {
    vi.setSystemTime(new Date('2024-01-15'));

    render(
      <BrowserRouter>
        <WritingPrompt />
      </BrowserRouter>
    );

    // Should render one of the prompts
    const prompts = [
      'What surprised you today?',
      'Describe a moment when you felt alive.',
      'What are you grateful for?',
    ];

    const foundPrompt = prompts.some(prompt =>
      screen.queryByText(prompt) !== null
    );

    expect(foundPrompt).toBe(true);
  });
});
```

**Step 2: Create WeeklyStats test**

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { WeeklyStats } from '../WeeklyStats';

// Mock useLanguage
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'dashboard.weeklyStats.streak': 'Streak',
        'dashboard.weeklyStats.streakDays': '{{count}} days',
        'dashboard.weeklyStats.thisWeek': 'This week',
        'dashboard.weeklyStats.words': '{{count}} words',
        'dashboard.weeklyStats.bestDay': 'Best day',
        'statistics.dayOfWeekChart.tuesdayAbbr': 'Tue',
      };
      return translations[key] || key;
    },
  }),
}));

describe('WeeklyStats', () => {
  const mockStats = {
    todayWords: 500,
    dailyGoal: 750,
    currentStreak: 5,
    longestStreak: 10,
    totalEntries: 50,
  };

  const mockWeeklyStats = {
    totalWords: 3420,
    bestDay: {
      date: '2024-01-15',
      words: 1200,
      weekday: 'tuesday',
    },
  };

  it('renders streak section', () => {
    render(
      <WeeklyStats stats={mockStats} weeklyStats={mockWeeklyStats} />
    );

    expect(screen.getByText('Streak')).toBeInTheDocument();
    expect(screen.getByText('5 days')).toBeInTheDocument();
  });

  it('renders words this week section', () => {
    render(
      <WeeklyStats stats={mockStats} weeklyStats={mockWeeklyStats} />
    );

    expect(screen.getByText('This week')).toBeInTheDocument();
    expect(screen.getByText('3,420 words')).toBeInTheDocument();
  });

  it('renders best day section with data', () => {
    render(
      <WeeklyStats stats={mockStats} weeklyStats={mockWeeklyStats} />
    );

    expect(screen.getByText('Best day')).toBeInTheDocument();
    expect(screen.getByText('1,200')).toBeInTheDocument();
    expect(screen.getByText('Tue')).toBeInTheDocument();
  });

  it('renders dash when no best day', () => {
    const emptyWeeklyStats = {
      totalWords: 0,
      bestDay: null,
    };

    render(
      <WeeklyStats stats={mockStats} weeklyStats={emptyWeeklyStats} />
    );

    expect(screen.getByText('—')).toBeInTheDocument();
  });
});
```

**Step 3: Run frontend tests**

Run: `cd frontend && npm run test:run`

Expected: All tests PASS

**Step 4: Commit**

```bash
git add frontend/src/components/dashboard/__tests__/
git commit -m "test: add frontend tests for WritingPrompt and WeeklyStats"
```

---

## Task 13: Final Integration Test

**Step 1: Run all backend tests**

Run: `uv run pytest -v`

Expected: All tests PASS

**Step 2: Run all frontend tests**

Run: `cd frontend && npm run test:run`

Expected: All tests PASS

**Step 3: Manual smoke test**

Run: `make dev`

1. Open http://localhost:5173
2. Log in to the app
3. Verify dashboard shows:
   - Writing prompt with daily inspiration
   - Featured entry (if 10+ entries exist)
   - Weekly stats in right panel (streak, words this week, best day)
4. Click "Show another" on featured entry
5. Verify different entry appears

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete dashboard redesign implementation"
```

---

## Summary

### Files Created
- `apps/journal/migrations/XXXX_featuredentry.py`
- `apps/api/tests/test_dashboard_featured.py`
- `frontend/src/components/dashboard/WritingPrompt.tsx`
- `frontend/src/components/dashboard/FeaturedEntry.tsx`
- `frontend/src/components/dashboard/WeeklyStats.tsx`
- `frontend/src/components/dashboard/__tests__/WritingPrompt.test.tsx`
- `frontend/src/components/dashboard/__tests__/WeeklyStats.test.tsx`

### Files Modified
- `apps/journal/models.py`
- `apps/api/views.py`
- `apps/api/urls.py`
- `frontend/src/hooks/useDashboard.ts`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/locales/cs.ts`
- `frontend/src/locales/en.ts`

### Commits (13 total)
1. `feat: add FeaturedEntry model for dashboard memories`
2. `test: add tests for dashboard featured entry and weekly stats`
3. `feat: add featured entry and weekly stats to dashboard`
4. `feat: add refresh-featured endpoint for dashboard`
5. `feat: add Czech translations for dashboard redesign`
6. `feat: add English translations for dashboard redesign`
7. `feat: extend useDashboard hook with featured entry and weekly stats`
8. `feat: add WritingPrompt component`
9. `feat: add FeaturedEntry component`
10. `feat: add WeeklyStats component`
11. `feat: update DashboardPage with new layout and components`
12. `test: add frontend tests for WritingPrompt and WeeklyStats`
13. `feat: complete dashboard redesign implementation`
