# Local Development Guide

Comprehensive guide for developing QuietPage locally with various workflow options.

## Prerequisites

- **Python 3.14+** with `uv` package manager
- **Node.js 18+** with npm
- **Redis** (optional, for full development mode with Celery)
- **Git** for version control

## Quick Start

### Initial Setup

```bash
# 1. Clone repository (if not already done)
git clone <repository-url>
cd QuietPage

# 2. Copy environment file
cp .env.example .env
# Edit .env and set SECRET_KEY, FERNET_KEY_PRIMARY

# 3. Install backend dependencies
uv pip install -r requirements/development.txt

# 4. Install frontend dependencies
cd frontend && npm install && cd ..

# 5. Run database migrations and create superuser
make setup

# 6. You're ready to develop!
make dev
```

Access the app at **http://localhost:5173**

## Development Workflows

QuietPage supports three development approaches. Choose based on your current needs:

### Option 1: Simple Local Development (Recommended)

**Best for:** Daily development, frontend/API work, feature development

**Services:**
- Django dev server (port 8000)
- Vite dev server (port 5173)
- SQLite database (embedded)
- In-memory cache (no Redis needed)

**Start command:**
```bash
make dev
```

**What it does:**
- Starts Django and Vite in a single terminal
- All service logs displayed with color coding
- Press Ctrl+C to stop all services

**Pros:**
- Fast startup
- No external dependencies
- Perfect for most development tasks

**Cons:**
- Cannot test async tasks (backups, reminders, cleanup)

---

### Option 2: Full Local Development

**Best for:** Testing Celery tasks, production-like behavior, background jobs

**Services:**
- Redis server
- Django dev server (port 8000)
- Vite dev server (port 5173)
- Celery worker (background tasks)
- Celery beat (scheduled tasks)
- SQLite database (or PostgreSQL if configured)
- Redis cache

**Start command:**
```bash
make dev-full
```

**What it does:**
- Starts all 5 services in a single terminal
- All service logs displayed with color coding
- Press Ctrl+C to stop all services

**Pros:**
- Complete feature set
- Test async tasks locally
- Redis-backed cache and task queue

**Cons:**
- Requires Redis installed locally
- Slightly slower startup

**Verify Celery is working:**
```bash
# In another terminal
make celery-status
```

---

### Option 3: Docker Development

**Best for:** Production-like environment, testing deployment, PostgreSQL needed

**Services:**
- PostgreSQL 16 database
- Redis 7
- Django (Gunicorn)
- Celery worker
- Celery beat

**Start command:**
```bash
docker-compose up
```

**Access:**
- Django API: http://localhost:8000/api/
- Frontend: Build separately with `cd frontend && npm run build`

**Pros:**
- Closest to production environment
- PostgreSQL instead of SQLite
- Isolated from local system

**Cons:**
- Slower startup
- Requires Docker Desktop
- Less convenient for rapid iteration

---

## Service Details

| Service | URL | Purpose |
|---------|-----|---------|
| Django API | http://localhost:8000 | Backend REST API |
| Vite Frontend | http://localhost:5173 | React SPA with hot reload |
| Vite Proxy | http://localhost:5173/api | Proxies to Django (port 8000) |
| Redis | localhost:6379 | Cache & Celery broker (full mode only) |

**Important:** Always access the app through **http://localhost:5173** during development. Vite proxies `/api` requests to Django automatically.

---

## Common Development Tasks

### Database Management

```bash
# Apply migrations
make migrate

# Create new migrations after model changes
make makemigrations

# Open Django shell
make shell

# Create additional superuser
make superuser
```

### Running Tests

**Backend tests:**
```bash
# Run all tests
make test

# Run specific test file
uv run pytest apps/journal/tests/test_models.py -v

# Run specific test
uv run pytest -k "test_streak" -v

# Run with markers
uv run pytest -m unit  # Only unit tests
uv run pytest -m encryption  # Only encryption tests
```

**Frontend tests:**
```bash
cd frontend

# Watch mode (interactive)
npm run test

# Single run (CI)
npm run test:run

# With coverage
npm run test:run -- --coverage
```

### Code Quality

```bash
# Format Python code
uv run black .

# Lint Python code
uv run flake8

# Lint frontend
cd frontend && npm run lint
```

### Translation Management

```bash
# Generate .po files
make messages

# Compile .mo files
make compilemessages
```

### Celery Task Management

```bash
# Start Celery worker manually
make celery-worker

# Start Celery beat manually
make celery-beat

# Check active tasks
make celery-status
```

---

## Manual Service Start (Alternative)

If you prefer separate terminal windows instead of `honcho`:

### Simple Development

**Terminal 1 - Django:**
```bash
make run
```

**Terminal 2 - Frontend:**
```bash
cd frontend && npm run dev
```

### Full Development

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Django:**
```bash
make run
```

**Terminal 3 - Frontend:**
```bash
cd frontend && npm run dev
```

**Terminal 4 - Celery Worker:**
```bash
make celery-worker
```

**Terminal 5 - Celery Beat:**
```bash
make celery-beat
```

---

## Environment Variables

Key variables in `.env`:

```bash
# Core Django settings
SECRET_KEY=<your-secret-key>
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development

# Encryption key for journal entries
FERNET_KEY_PRIMARY=<your-fernet-key>

# Optional: Redis (only needed for full development mode)
REDIS_URL=redis://localhost:6379
```

**Generate keys:**
```bash
# SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# FERNET_KEY_PRIMARY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Troubleshooting

### Port Already in Use

**Problem:** `Address already in use: 8000` or `Port 5173 is already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Find process using port 5173
lsof -ti:5173 | xargs kill -9
```

### Redis Connection Failed

**Problem:** `Error 61 connecting to localhost:6379. Connection refused.`

**Solution:**
```bash
# Check if Redis is installed
redis-server --version

# Install Redis (macOS)
brew install redis

# Start Redis manually
redis-server

# Or use simple dev mode instead
make dev  # No Redis needed
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### Frontend Proxy Errors

**Problem:** Frontend shows `502 Bad Gateway` or API errors

**Solution:**
- Ensure Django is running on port 8000
- Check terminal for Django errors
- Verify Vite proxy config in `frontend/vite.config.ts`

### Celery Tasks Not Running

**Problem:** Scheduled tasks don't execute

**Checklist:**
1. Redis is running: `redis-cli ping`
2. Celery worker is running: `make celery-status`
3. Celery beat is running (check terminal output)
4. Check for task errors in worker logs

### Database Migrations Out of Sync

**Problem:** `Migration foo conflicts with migration bar`

**Solution:**
```bash
# Reset database (development only!)
rm db.sqlite3
make migrate
make superuser
```

### Import Errors After Installing Dependencies

**Problem:** `ModuleNotFoundError: No module named 'foo'`

**Solution:**
```bash
# Reinstall dependencies
uv pip install -r requirements/development.txt

# Verify uv is using correct Python
uv run python --version
```

---

## Switching Between Workflows

You can freely switch between development modes:

### From Docker to Local:
```bash
# Stop Docker
docker-compose down

# Start local development
make dev
```

### From Simple to Full:
```bash
# Stop simple mode (Ctrl+C in terminal)
# Start full mode
make dev-full
```

### From Full to Simple:
```bash
# Stop full mode (Ctrl+C in terminal)
# Start simple mode
make dev
```

**Note:** Database is shared (db.sqlite3) across local modes, so data persists.

---

## Development Tips

1. **Use `make dev` for daily work** - it's fast and covers 90% of development needs
2. **Use `make dev-full` when testing background jobs** - backups, email reminders, cleanup tasks
3. **Use Docker for final testing** - before deploying to production
4. **Frontend hot reload** - Vite automatically reloads on file changes
5. **Django auto-reload** - Django dev server reloads on Python file changes
6. **Git hooks** - Consider setting up pre-commit hooks for code quality

### Recommended VSCode Extensions

- Python (Microsoft)
- ESLint
- Prettier
- Django Template
- Vite

### Recommended PyCharm/IntelliJ Plugins

- .env files support
- Django
- JavaScript and TypeScript

---

## Performance Notes

### Startup Times (Approximate)

- **Simple mode (`make dev`)**: ~3-5 seconds
- **Full mode (`make dev-full`)**: ~5-8 seconds
- **Docker mode (`docker-compose up`)**: ~20-30 seconds (first run), ~10 seconds (subsequent)

### Resource Usage

- **Simple mode**: ~500MB RAM
- **Full mode**: ~800MB RAM (Redis + Celery)
- **Docker mode**: ~1.5GB RAM (PostgreSQL + all services)

---

## Getting Help

- Check `make help` for all available commands
- Review `CLAUDE.md` for project guidelines
- Check `docs/SECURITY_CHECKLIST.md` for security best practices
- Report issues on GitHub

---

## Next Steps

After setting up local development:

1. Review the design system in `styles.md`
2. Explore the API at http://localhost:8000/api/
3. Review test coverage: `make test`
4. Try creating a journal entry via the UI
5. Experiment with different themes (Midnight/Paper)

Happy coding!
