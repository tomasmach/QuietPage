# AGENTS.md

This file provides coding guidelines for AI agents working in the QuietPage repository.

## Quick Reference

**Project:** QuietPage - Minimalist journaling app with encryption  
**Stack:** Django 6.0 (REST API) + React 19 + TypeScript + Vite  
**Key Features:** Field-level encryption (Fernet), timezone-aware streaks, session auth

---

## Build, Lint & Test Commands

### Backend (Django)

```bash
# Run all tests
pytest

# Run specific test file
pytest apps/journal/tests/test_models.py

# Run specific test function
pytest apps/journal/tests/test_models.py::TestEntryModel::test_word_count

# Run tests by marker
pytest -m unit              # Fast unit tests only
pytest -m integration       # Integration tests
pytest -m encryption        # Encryption-related tests
pytest -m streak            # Streak calculation tests

# Run with coverage (required: 80%+)
pytest --cov=apps --cov-report=html --cov-report=term-missing

# Skip coverage check for quick iteration
pytest --no-cov

# Database management
make migrate                # Apply migrations
make makemigrations         # Create migrations
make cache                  # Create cache table (required on first setup)

# Run dev server
make run                    # Django dev server (port 8000)
```

### Frontend (React + TypeScript)

```bash
cd frontend

# Development
npm run dev                 # Vite dev server (port 5173)

# Build & lint
npm run build               # TypeScript check + production build
npm run lint                # ESLint check

# Preview production build
npm run preview
```

**Development workflow:** Run Django (`make run`) + Vite (`npm run dev`) in separate terminals.

---

## Code Style Guidelines

### Backend (Python/Django)

**Imports:**
```python
# 1. Standard library
import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

# 2. Django
from django.db import models
from django.conf import settings
from django.utils import timezone

# 3. Third-party
from rest_framework import viewsets, status

# 4. Local apps
from apps.journal.models import Entry
from apps.api.serializers import EntrySerializer
```

**Module Documentation:**
- Every module MUST start with a module-level docstring
- Describe the module's purpose in 1-2 sentences

```python
"""
Journal models for QuietPage.

This module contains the Entry model with encryption support.
"""
```

**Classes & Methods:**
- Use class-based views (ViewSets/APIViews) for REST API
- Add docstrings to classes and complex methods
- Type hints encouraged in new code (not strictly enforced)

**String Literals:**
- User-facing messages: **Czech language** (e.g., `'Hodnocení musí být mezi 1 a 5.'`)
- Code comments/docstrings: English or Czech (prefer English for consistency)

**Model Patterns:**
```python
class MyModel(models.Model):
    def clean(self):
        """Model-level validation (runs in full_clean())."""
        super().clean()
        # Validation logic here
        if self.some_field and self.some_condition:
            raise ValidationError({'field': 'Chybová zpráva'})
    
    def save(self, *args, **kwargs):
        """Auto-calculate fields and run validation."""
        # Allow skipping validation for special cases
        skip_validation = kwargs.pop('skip_validation', False)
        if not skip_validation:
            self.full_clean()  # Calls clean()
        
        # Auto-calculate fields
        self.calculated_field = self.compute_value()
        super().save(*args, **kwargs)
```

**Timezone Handling:**
- ALWAYS use `timezone.now()` (not `datetime.now()`)
- ALWAYS use user's timezone for date calculations
- Streaks and "today" calculations MUST consider user timezone

```python
from zoneinfo import ZoneInfo
from django.utils import timezone

user_tz = ZoneInfo(str(user.timezone))
now = timezone.now().astimezone(user_tz)
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
```

**Database Queries:**
- Use `select_related()` for ForeignKey
- Use `prefetch_related()` for ManyToMany and reverse ForeignKey
- Filter early, order consistently

**Error Handling & Logging:**
```python
import logging
logger = logging.getLogger(__name__)

try:
    # Operation
    pass
except SpecificException as e:
    logger.exception('Descriptive error message')
    return Response({'status': 'error', 'message': 'User-facing Czech message'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### Frontend (React/TypeScript)

**Always follow `frontend/styles.md` for UI component patterns.**

**Imports:**
```typescript
// 1. React & external libraries
import { useState, useEffect, type ReactNode } from 'react';

// 2. Routing/contexts
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

// 3. Components (@ alias points to ./src)
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

// 4. Utils/lib
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

// 5. Icons (last)
import { Loader2, Check } from 'lucide-react';
```

**Component Structure:**
```typescript
// Export interface for component props
export interface MyComponentProps {
  variant?: 'primary' | 'secondary';
  children?: ReactNode;
}

// Use forwardRef for reusable UI components
const MyComponent = forwardRef<HTMLDivElement, MyComponentProps>(
  ({ variant = 'primary', children, ...props }, ref) => {
    return (
      <div ref={ref} {...props}>
        {children}
      </div>
    );
  }
);

MyComponent.displayName = 'MyComponent';

export { MyComponent };
```

**TypeScript:**
- Strict mode enabled (no `any` types)
- Define interfaces for all API responses
- Use `type` for unions, `interface` for objects

**Styling:**
- Use Tailwind CSS classes (no inline styles)
- Use `cn()` utility for conditional classes
- Follow brutalist design tokens from `styles.md`

**Error Handling:**
```typescript
try {
  const data = await api.post('/endpoint', payload);
  // Success
} catch (error) {
  const errorData = JSON.parse((error as Error).message);
  // Handle error - show toast, update UI state
}
```

---

## Security Best Practices

### Backend

1. **Encryption:** Entry content is encrypted at rest via `EncryptedTextField`
   - NEVER filter or order by encrypted fields (encryption is non-deterministic)
   - Do NOT log decrypted content
   
2. **Authentication:**
   - ALWAYS use `IsAuthenticated` permission on API views
   - Filter querysets by `user=self.request.user`
   - Never trust client-provided user IDs
   
3. **CSRF Protection:**
   - CSRF token handled automatically by API client
   - NEVER disable CSRF on state-changing endpoints
   
4. **Rate Limiting:**
   - Apply throttling to create/update actions
   - Use `ScopedRateThrottle` for granular control
   
5. **Atomic Transactions:**
   - Use `transaction.atomic()` for multi-step operations
   - Use `select_for_update()` for concurrent updates

### Frontend

1. **API Client:** Always use singleton `api` instance (handles CSRF automatically)
2. **XSS Prevention:** React escapes by default - NEVER use `dangerouslySetInnerHTML`
3. **Credentials:** `credentials: 'include'` for session cookies (already in api.ts)
4. **Sensitive Data:** Never log user content or tokens

---

## Environment & Dependencies

**Required Environment Variables:**
- `SECRET_KEY` - Django secret (50+ chars)
- `FERNET_KEY_PRIMARY` - Encryption key (44 bytes base64, use `Fernet.generate_key()`)

**Database Cache:** 
- MUST run `make cache` after first migration to create `cache_table`
- Project uses database cache (no Redis required)

**Encryption Key Rotation:**
- NEVER change `FERNET_KEY_PRIMARY` in production (makes old data unreadable)
- Key rotation requires migration strategy

---

## Git Workflow

**Committing:**
- NEVER commit code automatically
- ALWAYS propose commit message to user and wait for approval
- Format: `<type>: <description>` (e.g., `feat: add mood analytics chart`)
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `style`, `perf`

**Files to Never Commit:**
- `.env` (contains secrets)
- `credentials.json`, `*.key`, `*.pem`
- `htmlcov/`, `__pycache__/`, `*.pyc`
- `frontend/dist/`, `staticfiles/`

---

## Common Pitfalls & Important Notes

1. **Custom User Model:** `AUTH_USER_MODEL = 'accounts.User'` - NEVER reference `auth.User`
2. **Streak Calculation:** Handled by signals.py - updates on Entry creation when `word_count > 0`
3. **Vite Manifest:** Production requires `npm run build` before `collectstatic`
4. **Catch-all Route:** SPA catch-all MUST be last in `urls.py` (or it catches Django routes)
5. **Tags:** Entry uses django-taggit with custom `UUIDTaggedItem` (UUID primary keys)
6. **Empty Content:** Allowed for 750words.com style - streak only updates when `word_count > 0`

---

## Testing Requirements

- **Coverage:** Minimum 80% (enforced by pytest.ini)
- **Markers:** Tag tests appropriately (`@pytest.mark.unit`, `@pytest.mark.encryption`, etc.)
- **Database:** Use `--reuse-db` for speed (already in pytest.ini)
- **Isolation:** Unit tests should not hit database (use mocks)
- **Timezone:** Test streak logic with multiple timezones

---

## Reference Files

- **Full setup guide:** `CLAUDE.md`
- **Frontend styling:** `frontend/styles.md`
- **API endpoints:** `apps/api/views.py`
- **Encryption:** `apps/journal/fields.py` (EncryptedTextField)
