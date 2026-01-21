# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QuietPage is a journaling and mindfulness application with a Django REST API backend and React SPA frontend. The app features encrypted journal entries, streak tracking, mood analytics, and a distinctive "analog tech" design aesthetic.

## Git Workflow

- The **main development branch** is `dev` (not `main`)
- **All new branches** should be created from `dev`
- **All pull requests** should target `dev` (unless explicitly stated otherwise)
- Use `main` branch only for production releases

## Development Guidelines

- Always use best coding practices with a security-first approach
- Always use Context7 MCP when library/API documentation, code generation, setup or configuration steps are needed without requiring explicit user request
- This project uses `uv` package manager with Python 3.14 - use `uv` for running Python commands, tests, and package management
- No need to activate `.venv/bin/activate` when using `uv run` - it automatically uses the project's virtual environment

## Development Commands

### Quick Start Workflows

```bash
make install-dev       # Install all dependencies (Python + Node.js)
make setup             # Initial setup (migrate + superuser)
make dev               # Start development (Django + Vite)
make dev-full          # Start full stack (Redis + Django + Vite + Celery)
```

### Backend (Django)

```bash
make run               # Start dev server (port 8000)
make migrate           # Apply migrations
make makemigrations    # Create new migrations
make shell             # Django interactive shell
make messages          # Generate translation files
make compilemessages   # Compile translations
```

Run specific tests:
```bash
uv run pytest apps/journal/tests/test_models.py -v
uv run pytest -k "test_streak" -v
uv run pytest -m unit  # Run only unit tests
```

Note: `make test` uses Django's test runner. For pytest with markers and coverage, use `uv run pytest` directly.

### Frontend (React)

```bash
cd frontend
npm run dev            # Start dev server (port 5173, proxies /api to 8000)
npm run build          # Production build
npm run lint           # ESLint
npm run test           # Vitest watch mode
npm run test:run       # Single test run (CI)
```

For detailed setup instructions and troubleshooting, reference `docs/LOCAL_DEVELOPMENT.md`.

## Architecture

### Backend Structure

- `apps/accounts/` - User model, authentication, profile management
- `apps/journal/` - Entry model with encryption, word counting, streaks
- `apps/api/` - REST endpoints, serializers, statistics views
- `apps/core/` - Infrastructure tasks (Celery tasks for backups, cleanup, reminders)
- `config/` - Django settings (base, development, production)

Key patterns:
- **Per-user encryption**: Each user has unique encryption key in `EncryptionKey` model. Entry content encrypted/decrypted in `Entry.save()` and `Entry.get_content()` using user's personal key (Fernet: AES-128-CBC + HMAC-SHA256)
- **Master key encryption**: User encryption keys are themselves encrypted with master key (`FIELD_ENCRYPTION_KEY`) before storage
- **Word counting**: Calculated in `Entry.save()` before encryption (must access plaintext)
- Signal handlers for user encryption key creation (`apps/accounts/signals.py`) and streak updates (`apps/journal/signals.py`)
- Factory fixtures for testing (`conftest.py`)
- Celery tasks for async operations (requires Redis in full mode)

### Frontend Structure

- `src/pages/` - Route components (Dashboard, Entry, Stats, Archive, Settings)
- `src/components/` - UI components organized by feature (auth, journal, statistics, ui)
- `src/hooks/` - Custom hooks (useAutoSave, useEntry, useStatistics, useDashboard)
- `src/contexts/` - Global state (Auth, Theme, Language, Toast)

Path alias: `@/*` maps to `src/*`

Tech stack: React 19 + TypeScript + Tailwind CSS + Vite

### API Communication

Frontend proxies `/api` requests to Django backend at localhost:8000 (configured in `vite.config.ts`). Always access the app through http://localhost:5173 during development, not port 8000.

## Design System

The app uses an "analog tech" aesthetic inspired by an architect's drafting table or terminal:
- IBM Plex Mono font throughout (monospace for everything)
- Two themes: Midnight (dark, priority) and Paper (light)
- Hard borders (no rounded corners), hard shadows (4px offset with `shadow-hard`)
- No gradients, blur effects, or soft shadows
- Theme switching via `data-theme` attribute on root element
- CSS variables defined in `index.css` for semantic colors (bg-app, bg-panel, text-main, text-muted, accent, border)

Reference `styles.md` for complete design rules and component guidelines.

## Testing

Backend: pytest with 80% coverage threshold
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Domain markers: `@pytest.mark.encryption`, `@pytest.mark.streak`, `@pytest.mark.statistics`

Frontend: Vitest with React Testing Library
- Tests in `__tests__/` subdirectories adjacent to components
- Mock contexts via `vitest.mock()` (e.g., useLanguage)

## Key Domain Concepts

- **Entry encryption**: Server-side per-user Fernet encryption. Each user has unique encryption key stored in `EncryptionKey` model (encrypted with master key). Entry content encrypted in `Entry.save()` and decrypted via `Entry.get_content()`. Cannot filter/order by encrypted fields. Master key set via `FIELD_ENCRYPTION_KEY` env var.
- **Goal streaks**: Consecutive days meeting word count goal (default 750 words). Calculated and cached on entry save.
- **Word counting**: Calculated in `Entry.save()` before encryption (requires plaintext access). Counts words in entry content.
- **Statistics**: Heatmaps (calendar view), mood charts (over time), tag analytics (frequency/usage), personal records (longest streak, most words, etc.)
- **Cache**: Development uses LocMemCache (in-memory, no setup). Production uses Redis. No database cache table needed.
- **Celery tasks**: Background jobs for backups, cleanup, and reminders. Require Redis and run via `make dev-full` or Docker.

## Environment Setup

Required for development:
```bash
cp .env.example .env
# Edit .env with required values (SECRET_KEY, FIELD_ENCRYPTION_KEY)
make setup
```

Production requires PostgreSQL and additional security settings (see `docs/SECURITY_CHECKLIST.md`).
