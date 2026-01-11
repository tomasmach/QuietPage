#!/bin/bash
# Docker entrypoint script for QuietPage
# Handles database migrations and static file collection before starting the application

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== QuietPage Docker Entrypoint ===${NC}"

# Check if this is the web service (not celery worker/beat)
# We only want to run migrations and collectstatic for the web service
if [ "${DJANGO_SERVICE}" = "web" ] || [ "$1" = "gunicorn" ]; then
    echo -e "${YELLOW}Running database migrations...${NC}"
    python manage.py migrate --noinput

    echo -e "${YELLOW}Collecting static files...${NC}"
    python manage.py collectstatic --noinput --clear

    echo -e "${GREEN}Setup complete!${NC}"
fi

# Execute the main command (gunicorn, celery, etc.)
echo -e "${GREEN}Starting: $@${NC}"
exec "$@"
