# Dashboard Redesign

## Overview

Redesign dashboardu pro QuietPage - přeměna z pasivní stránky na inspirativní hub, který motivuje k psaní.

## Nové prvky

### 1. Denní Writing Prompt
- Statický seznam ~50 promptů v translation souborech
- Rotace podle dne v roce (`dayOfYear % prompts.length`)
- Karta s ikonou, textem promptu a CTA "Začít psát"

### 2. Featured Entry z historie
- Náhodný zápis z minulosti zobrazený na dashboardu
- Podmínka: uživatel má alespoň 10 zápisů
- Konzistentní přes celý den a všechna zařízení (uloženo v DB)
- Tlačítko "Zobrazit jiný" pro refresh

### 3. Weekly Stats (3 statistiky)
- Aktuální streak ("5 dní")
- Slov tento týden ("3 420 slov")
- Nejlepší den tento týden ("1 203 slov - úterý")

## Datový model

### Nový model `FeaturedEntry`

```python
class FeaturedEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='featured_entries')
    date = models.DateField(help_text="Date in user's timezone")
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']
        indexes = [models.Index(fields=['user', 'date'])]
```

## API

### Dashboard endpoint rozšíření (`GET /api/v1/dashboard/`)

Response rozšířena o:
```json
{
    "featured_entry": {
        "id": 123,
        "title": "...",
        "content_preview": "...",
        "created_at": "2024-03-15T...",
        "word_count": 542,
        "days_ago": 285
    },
    "weekly_stats": {
        "total_words": 3420,
        "best_day": {
            "date": "2024-01-10",
            "words": 1203,
            "weekday": "wednesday"
        }
    }
}
```

### Nový endpoint (`POST /api/v1/dashboard/refresh-featured/`)

Vygeneruje nový featured entry pro dnešek (jiný než aktuální).

## Frontend komponenty

### Nové komponenty

- `src/components/dashboard/WritingPrompt.tsx` - denní prompt s CTA
- `src/components/dashboard/FeaturedEntry.tsx` - karta se starým zápisem
- `src/components/dashboard/WeeklyStats.tsx` - 3 statistiky v context panelu

### Změny v existujících

- `DashboardPage.tsx` - nový layout hlavní oblasti
- `StatsPanel.tsx` - nahradit/zjednodušit na WeeklyStats
- `useDashboard.ts` - přidat featuredEntry, weeklyStats, refreshFeaturedEntry()

## Layout

### Hlavní oblast (střed)
1. Greeting + dnešní progress (existující)
2. Writing prompt karta
3. Featured entry karta

### Context panel (pravý sidebar)
1. Weekly stats (streak, slov tento týden, nejlepší den)
2. Případně zjednodušený recent entries

## i18n

Prompty a všechny texty v translation souborech:

```json
{
    "dashboard": {
        "writingPrompt": {
            "title": "Dnešní inspirace",
            "cta": "Začít psát"
        },
        "featuredEntry": {
            "title": "Z tvé historie",
            "daysAgo": "před {{count}} dny",
            "refresh": "Zobrazit jiný"
        },
        "weeklyStats": {
            "streak": "Série",
            "thisWeek": "Tento týden",
            "bestDay": "Nejlepší den"
        },
        "prompts": [
            "Co tě dnes překvapilo?",
            "..."
        ]
    }
}
```

## Backend logika

### Featured entry výběr

1. Request na dashboard
2. Zkontrolovat: existuje FeaturedEntry pro dnešek (v user TZ)?
   - Ano → vrátit
   - Ne → vybrat random entry, uložit, vrátit
3. Refresh endpoint: smazat aktuální, vybrat nový (jiný), uložit

### Cleanup task

Celery task pro mazání starých FeaturedEntry záznamů (>7 dní).

## Edge cases

| Situace | Chování |
|---------|---------|
| Méně než 10 zápisů | featuredEntry: null, sekce se nezobrazí |
| Featured entry smazán | Při dalším requestu se vybere nový |
| Refresh s 1 entry | Vrátí stejný (není alternativa) |
| Nový den (půlnoc v user TZ) | Nový featured při prvním requestu |

## Testy

### Backend (pytest)
- `test_featured_entry_created_on_first_request`
- `test_featured_entry_consistent_across_requests`
- `test_featured_entry_requires_min_10_entries`
- `test_refresh_featured_returns_different_entry`
- `test_weekly_stats_calculation`

### Frontend (vitest)
- WritingPrompt renderuje správný prompt pro den
- FeaturedEntry zobrazuje data, loading state, refresh
- WeeklyStats zobrazuje všechny 3 statistiky

## Design System

Dodržovat styles.md:
- IBM Plex Mono font
- Hard borders (border-2), no rounded corners
- shadow-hard pro karty
- Semantic colors přes CSS variables
