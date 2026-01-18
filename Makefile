# QuietPage - Makefile
# Shortcuts for common Django management commands

# Development workflow targets
.PHONY: help install-dev dev dev-full

# Django management targets
.PHONY: setup run migrate makemigrations shell test collectstatic superuser

# Translation targets
.PHONY: messages compilemessages

# Celery targets
.PHONY: celery-worker celery-beat celery-status

# Production targets
.PHONY: setup-prod deploy backup backup-list

help:
	@echo "QuietPage - Available commands:"
	@echo ""
	@echo "Development workflow:"
	@echo "  make install-dev      - Install all development dependencies"
	@echo "  make dev              - Start development (Django + Vite)"
	@echo "  make dev-full         - Start full stack (Redis + Django + Vite + Celery)"
	@echo ""
	@echo "Django commands:"
	@echo "  make setup            - Initial setup (migrate + superuser)"
	@echo "  make run              - Run development server"
	@echo "  make migrate          - Apply database migrations"
	@echo "  make makemigrations   - Create new migrations"
	@echo "  make superuser        - Create superuser account"
	@echo "  make shell            - Open Django shell"
	@echo "  make test             - Run tests"
	@echo "  make collectstatic    - Collect static files"
	@echo ""
	@echo "Translation commands:"
	@echo "  make messages         - Generate translation files (.po)"
	@echo "  make compilemessages  - Compile translation files (.mo)"
	@echo ""
	@echo "Celery commands:"
	@echo "  make celery-worker    - Start Celery worker"
	@echo "  make celery-beat      - Start Celery beat scheduler"
	@echo "  make celery-status    - Show active Celery tasks"
	@echo ""
	@echo "Production commands:"
	@echo "  make setup-prod       - Initial production setup (Docker)"
	@echo "  make deploy           - Deploy updates with zero downtime"
	@echo "  make backup           - Create database and media backup"
	@echo "  make backup-list      - List all existing backups"

# Run development server
run:
	uv run python manage.py runserver

# Initial project setup
setup:
	@echo "Setting up QuietPage..."
	@echo "Step 1: Applying database migrations..."
	uv run python manage.py migrate
	@echo "Migrations complete."
	@echo ""
	@echo "Step 2: Creating superuser..."
	uv run python manage.py createsuperuser
	@echo ""
	@echo "Setup complete! Run 'make dev' to start development."

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
	@echo "Running production setup..."
	./scripts/setup.sh

deploy:
	@echo "Deploying QuietPage..."
	./scripts/deploy.sh

backup:
	@echo "Creating backup..."
	./scripts/backup.sh

backup-list:
	@echo "Listing backups..."
	./scripts/backup.sh --list

# Development workflow commands
install-dev:
	@echo "Installing development dependencies..."
	uv pip install -r requirements/development.txt
	cd frontend && npm install
	@echo "Dependencies installed!"

dev:
	@echo "Starting development server..."
	@echo "Django: http://localhost:8000 | Vite: http://localhost:5173"
	uv run honcho start -f Procfile.dev

dev-full:
	@echo "Starting full development stack..."
	@echo "Django: http://localhost:8000 | Vite: http://localhost:5173 | Redis + Celery"
	uv run honcho start -f Procfile.full
