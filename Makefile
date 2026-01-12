# QuietPage - Makefile
# Shortcuts for common Django management commands

.PHONY: help setup run migrate makemigrations shell test collectstatic messages compilemessages cache superuser celery-worker celery-beat celery-status setup-prod deploy backup backup-list install-dev dev dev-full

help:
	@echo "QuietPage - Available commands:"
	@echo ""
	@echo "Development workflow:"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make dev              - Start development (Django + Vite)"
	@echo "  make dev-full         - Start full development (Redis + Django + Vite + Celery)"
	@echo ""
	@echo "Basic commands:"
	@echo "  make setup            - Complete initial setup (migrate + superuser)"
	@echo "  make run              - Run development server"
	@echo "  make migrate          - Apply database migrations"
	@echo "  make makemigrations   - Create new migrations"
	@echo "  make superuser        - Create superuser account"
	@echo "  make shell            - Open Django shell"
	@echo "  make test             - Run tests"
	@echo "  make collectstatic    - Collect static files"
	@echo "  make messages         - Generate translation files (.po)"
	@echo "  make compilemessages  - Compile translation files (.mo)"
	@echo ""
	@echo "Celery commands:"
	@echo "  make celery-worker    - Start Celery worker"
	@echo "  make celery-beat      - Start Celery beat scheduler"
	@echo "  make celery-status    - Show active Celery tasks"
	@echo ""
	@echo "Production deployment commands:"
	@echo "  make setup-prod       - Initial production setup (Docker)"
	@echo "  make deploy           - Deploy updates with zero downtime"
	@echo "  make backup           - Create database and media backup"
	@echo "  make backup-list      - List all existing backups"

# Run development server
run:
	uv run python manage.py runserver

# Initial project setup
setup:
	@echo "🚀 Spouštím kompletní setup projektu QuietPage..."
	@echo "1️⃣ Aplikuji migrace databáze..."
	uv run python manage.py migrate
	@echo "✓ Migrace dokončeny\n"
	@echo "2️⃣ Vytváření superuživatele..."
	uv run python manage.py createsuperuser
	@echo "\n✅ Setup dokončen! Můžete spustit server pomocí: make run"

# Database migrations
migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

# Create superuser
superuser:
	uv run python manage.py createsuperuser

# Django shell
shell:
	uv run python manage.py shell

# Run tests
test:
	uv run python manage.py test

# Static files
collectstatic:
	uv run python manage.py collectstatic --noinput

# Translation commands
messages:
	uv run python manage.py makemessages -l cs --ignore=venv --ignore=staticfiles

compilemessages:
	uv run python manage.py compilemessages --ignore=venv

# Celery commands
celery-worker:
	uv run celery -A config worker --loglevel=info

celery-beat:
	uv run celery -A config beat --loglevel=info

celery-status:
	uv run celery -A config inspect active

# Production deployment scripts
setup-prod:
	@echo "🚀 Running production setup..."
	./scripts/setup.sh

deploy:
	@echo "🚀 Deploying QuietPage..."
	./scripts/deploy.sh

backup:
	@echo "💾 Creating backup..."
	./scripts/backup.sh

backup-list:
	@echo "📋 Listing backups..."
	./scripts/backup.sh --list

# Development workflow commands
install-dev:
	@echo "📦 Installing development dependencies..."
	uv pip install -r requirements/development.txt
	@echo "✅ Development dependencies installed!"

dev:
	@echo "🚀 Starting simple development environment (Django + Vite)..."
	@echo "Services: Django (http://localhost:8000) + Vite (http://localhost:5173)"
	uv run honcho start

dev-full:
	@echo "🚀 Starting full development environment (Redis + Django + Vite + Celery)..."
	@echo "Services: Redis + Django (http://localhost:8000) + Vite (http://localhost:5173) + Celery Worker + Celery Beat"
	uv run honcho start -f Procfile.full
