# Local Development Guide

Guide for developing QuietPage locally with various workflow options.

## Prerequisites

- **Python 3.14+** with `uv` package manager
- **Node.js 18+** with npm
- **Redis** (optional, for full development mode)
- **Git**

## Quick Start

```bash
# Clone and enter repository
git clone <repository-url>
cd QuietPage

# Copy environment file and configure
cp .env.example .env
# Edit .env: set SECRET_KEY and FERNET_KEY_PRIMARY

# Install all dependencies
make install-dev

# Run migrations and create superuser
make setup

# Start development
make dev
```

Access the app at **http://localhost:5173**

## Development Workflows

Choose the approach that fits your current needs:

### Option 1: Simple Development (Recommended)

Best for daily development, frontend/API work, and feature development.

```bash
make dev
```

**Services:** Django (8000) + Vite (5173) + SQLite + in-memory cache

- Fast startup, no external dependencies
- Cannot test async tasks (backups, reminders, cleanup)

---

### Option 2: Full Development

Best for testing Celery tasks, background jobs, and production-like behavior.

```bash
make dev-full
```

**Services:** Redis + Django + Vite + Celery worker + Celery beat

- Complete feature set with Redis-backed cache and task queue
- Requires Redis installed locally

Verify Celery is working:
```bash
make celery-status
```

---

### Option 3: Docker Development

Best for production-like environment with PostgreSQL.

```bash
docker-compose up
```

**Services:** PostgreSQL 16 + Redis 7 + Django (Gunicorn) + Celery

- Closest to production, isolated from local system
- Slower startup, requires Docker Desktop

---

## Service Details

| Service | URL | Purpose |
|---------|-----|---------|
| Django API | http://localhost:8000 | Backend REST API |
| Vite Frontend | http://localhost:5173 | React SPA with hot reload |
| Vite Proxy | http://localhost:5173/api | Proxies to Django |
| Redis | localhost:6379 | Cache & Celery broker (full mode) |

**Note:** Always access the app through **http://localhost:5173** during development. Vite proxies `/api` requests to Django automatically.

---

## Common Tasks

### Database
```bash
make migrate          # Apply migrations
make makemigrations   # Create new migrations
make shell            # Open Django shell
make superuser        # Create superuser
```

### Testing

**Backend:**
```bash
make test                                          # Run all tests
uv run pytest apps/journal/tests/test_models.py -v # Specific file
uv run pytest -k "test_streak" -v                  # By name
uv run pytest -m unit                              # By marker
```

**Frontend:**
```bash
cd frontend
npm run test          # Watch mode
npm run test:run      # Single run (CI)
```

### Code Quality
```bash
uv run black .                    # Format Python
uv run flake8                     # Lint Python
cd frontend && npm run lint       # Lint frontend
```

### Translations
```bash
make messages         # Generate .po files
make compilemessages  # Compile .mo files
```

### Celery
```bash
make celery-worker    # Start worker
make celery-beat      # Start scheduler
make celery-status    # Check active tasks
```

---

## Manual Service Start

If you prefer separate terminals instead of honcho:

**Simple mode:**
```bash
# Terminal 1
make run
# Terminal 2
cd frontend && npm run dev
```

**Full mode:** Add redis-server, make celery-worker, and make celery-beat in separate terminals.

---

## Environment Variables

Key variables in `.env`:

```bash
SECRET_KEY=<your-secret-key>
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
FERNET_KEY_PRIMARY=<your-fernet-key>
REDIS_URL=redis://localhost:6379  # Optional, for full mode
```

**Generate keys:**
```bash
# SECRET_KEY
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# FERNET_KEY_PRIMARY
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Troubleshooting

### Port Already in Use

```bash
lsof -ti:8000 | xargs kill -9   # Kill process on port 8000
lsof -ti:5173 | xargs kill -9   # Kill process on port 5173
```

### Redis Connection Failed

```bash
brew install redis    # Install Redis (macOS)
redis-server          # Start Redis
redis-cli ping        # Verify (should return PONG)
```

Or use `make dev` which does not require Redis.

### Frontend Proxy Errors (502 Bad Gateway)

- Ensure Django is running on port 8000
- Check terminal for Django errors
- Verify Vite proxy config in `frontend/vite.config.ts`

### Celery Tasks Not Running

1. Redis is running: `redis-cli ping`
2. Celery worker is running: `make celery-status`
3. Celery beat is running (check terminal output)

### Database Migration Conflicts

```bash
rm db.sqlite3         # Reset database (development only)
make migrate
make superuser
```

### Module Not Found Errors

```bash
make install-dev      # Reinstall all dependencies
uv run python --version
```

---

## Switching Between Workflows

Switch freely between modes - just Ctrl+C and run the new command:

```bash
docker-compose down && make dev       # Docker to local
make dev-full                         # Simple to full
make dev                              # Full to simple
```

Database (db.sqlite3) is shared across local modes, so data persists.

---

## Tips

- Use `make dev` for daily work (fast, covers 90% of needs)
- Use `make dev-full` when testing background jobs
- Use Docker for final testing before production
- Both Django and Vite auto-reload on file changes

**Recommended VSCode extensions:** Python, ESLint, Prettier, Django Template

---

## Performance

| Mode | Startup | RAM |
|------|---------|-----|
| Simple (`make dev`) | ~3-5s | ~500MB |
| Full (`make dev-full`) | ~5-8s | ~800MB |
| Docker | ~10-30s | ~1.5GB |

---

## Getting Help

- `make help` - List all commands
- `CLAUDE.md` - Project guidelines
- `docs/SECURITY_CHECKLIST.md` - Security best practices

## Next Steps

1. Review design system in `styles.md`
2. Explore API at http://localhost:8000/api/
3. Run tests: `make test`
4. Create a journal entry
5. Try both themes (Midnight/Paper)
