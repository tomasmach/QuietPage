# QuietPage - Makefile
# Shortcuts for common Django management commands

.PHONY: help setup run migrate makemigrations shell test collectstatic messages compilemessages cache superuser

help:
	@echo "QuietPage - Available commands:"
	@echo "  make setup            - Complete initial setup (migrate + cache table + superuser)"
	@echo "  make run              - Run development server"
	@echo "  make migrate          - Apply database migrations"
	@echo "  make makemigrations   - Create new migrations"
	@echo "  make cache            - Create cache table (required for first setup)"
	@echo "  make superuser        - Create superuser account"
	@echo "  make shell            - Open Django shell"
	@echo "  make test             - Run tests"
	@echo "  make collectstatic    - Collect static files"
	@echo "  make messages         - Generate translation files (.po)"
	@echo "  make compilemessages  - Compile translation files (.mo)"

# Run development server
run:
	python manage.py runserver

# Initial project setup
setup:
	@echo "🚀 Spouštím kompletní setup projektu QuietPage..."
	@echo "1️⃣ Aplikuji migrace databáze..."
	python manage.py migrate
	@echo "✓ Migrace dokončeny\n"
	@echo "2️⃣ Vytvářím cache tabulku..."
	python manage.py createcachetable
	@echo "✓ Cache tabulka vytvořena\n"
	@echo "3️⃣ Vytváření superuživatele..."
	python manage.py createsuperuser
	@echo "\n✅ Setup dokončen! Můžete spustit server pomocí: make run"

# Database migrations
migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

# Create cache table (required for database cache backend)
cache:
	@echo "📦 Vytvářím cache tabulku..."
	python manage.py createcachetable
	@echo "✓ Cache tabulka úspěšně vytvořena"

# Create superuser
superuser:
	python manage.py createsuperuser

# Django shell
shell:
	python manage.py shell

# Run tests
test:
	python manage.py test

# Static files
collectstatic:
	python manage.py collectstatic --noinput

# Translation commands
messages:
	python manage.py makemessages -l cs --ignore=venv --ignore=staticfiles

compilemessages:
	python manage.py compilemessages --ignore=venv
