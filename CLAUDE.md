# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QuietPage is a journaling and mindfulness application with a Django REST API backend and React SPA frontend. The app features encrypted journal entries, streak tracking, mood analytics, and a distinctive "analog tech" design aesthetic.

## Development Guidelines

- Always use best coding practices with a security-first approach
- Always use Context7 MCP when library/API documentation, code generation, setup or configuration steps are needed without requiring explicit user request

## Development Commands

### Backend (Django)

```bash
make setup             # Initial setup (migrate + cache + superuser)
make run               # Start dev server (port 8000)
make migrate           # Apply migrations
make makemigrations    # Create new migrations
make test              # Run tests with coverage
make shell             # Django interactive shell
make messages          # Generate translation files
make compilemessages   # Compile translations
```

Run specific tests:
```bash
pytest apps/journal/tests/test_models.py -v
pytest -k "test_streak" -v
pytest -m unit  # Run only unit tests
```

### Frontend (React)

```bash
cd frontend
npm run dev            # Start dev server (port 5173, proxies /api to 8000)
npm run build          # Production build
npm run lint           # ESLint
npm run test           # Vitest watch mode
npm run test:run       # Single test run (CI)
```

## Architecture

### Backend Structure

- `apps/accounts/` - User model, authentication, profile management
- `apps/journal/` - Entry model with encryption, word counting, streaks
- `apps/api/` - REST endpoints, serializers, statistics views
- `config/` - Django settings (base, development, production)

Key patterns:
- Custom `EncryptedTextField` in `apps/journal/fields.py` using Fernet encryption
- Signal handlers for auto word-count and encryption (`apps/journal/signals.py`)
- Factory fixtures for testing (`conftest.py`)

### Frontend Structure

- `src/pages/` - Route components (Dashboard, Entry, Stats, Archive, Settings)
- `src/components/` - UI components organized by feature (auth, journal, statistics, ui)
- `src/hooks/` - Custom hooks (useAutoSave, useEntry, useStatistics, useDashboard)
- `src/contexts/` - Global state (Auth, Theme, Language, Toast)

Path alias: `@/*` maps to `src/*`

### API Communication

Frontend proxies `/api` requests to Django backend at localhost:8000 (configured in `vite.config.ts`).

## Design System

The app uses an "analog tech" aesthetic with:
- IBM Plex Mono font throughout
- Two themes: Midnight (dark, default) and Paper (light)
- Hard borders (no rounded corners), hard shadows (4px offset)
- No gradients or blur effects

Theme switching via `data-theme` attribute on root element. CSS variables defined in `index.css`.

Reference `styles.md` for detailed design guidelines.

## Testing

Backend: pytest with 80% coverage threshold
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Domain markers: `@pytest.mark.encryption`, `@pytest.mark.streak`, `@pytest.mark.statistics`

Frontend: Vitest with React Testing Library
- Tests in `__tests__/` subdirectories adjacent to components
- Mock contexts via `vitest.mock()` (e.g., useLanguage)

## Key Domain Concepts

- **Entry encryption**: Server-side Fernet encryption via custom field
- **Goal streaks**: Consecutive days meeting word count goal (default 750 words)
- **Word counting**: Automatic via Django signal on entry save
- **Statistics**: Heatmaps, mood charts, tag analytics, personal records

## Environment Setup

Required for development:
```bash
cp .env.example .env
# Edit .env with required values (SECRET_KEY, FERNET_KEY_PRIMARY)
make setup
```

Production requires PostgreSQL and additional security settings (see `docs/SECURITY_CHECKLIST.md`).
