# QuietPage - Makefile
# Shortcuts for common Django management commands

.PHONY: help run migrate makemigrations shell test collectstatic messages compilemessages

help:
	@echo "QuietPage - Available commands:"
	@echo "  make run              - Run development server"
	@echo "  make migrate          - Apply database migrations"
	@echo "  make makemigrations   - Create new migrations"
	@echo "  make shell            - Open Django shell"
	@echo "  make test             - Run tests"
	@echo "  make collectstatic    - Collect static files"
	@echo "  make messages         - Generate translation files (.po)"
	@echo "  make compilemessages  - Compile translation files (.mo)"

# Run development server
run:
	python manage.py runserver

# Database migrations
migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

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
