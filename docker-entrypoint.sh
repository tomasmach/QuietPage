#!/bin/bash
# Docker entrypoint script for QuietPage
# Handles database migrations and static file collection before starting the application

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== QuietPage Docker Entrypoint ===${NC}"

# Substitute environment variables in nginx config if they exist
if [ -n "$SSL_CERT_PATH" ] && [ -n "$SSL_KEY_PATH" ]; then
    echo -e "${YELLOW}Substituting SSL certificate paths in nginx configuration...${NC}"
    if [ -f /etc/nginx/conf.d/quietpage.conf.template ]; then
        envsubst '$SSL_CERT_PATH $SSL_KEY_PATH' < /etc/nginx/conf.d/quietpage.conf.template > /etc/nginx/conf.d/quietpage.conf
        echo -e "${GREEN}SSL paths configured: $SSL_CERT_PATH${NC}"
    fi
elif [ -f /etc/nginx/conf.d/quietpage.conf.template ]; then
    echo -e "${YELLOW}WARNING: SSL_CERT_PATH and SSL_KEY_PATH not set. Using template as-is.${NC}"
    cp /etc/nginx/conf.d/quietpage.conf.template /etc/nginx/conf.d/quietpage.conf
fi

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
echo -e "${GREEN}Starting: $*${NC}"

# If command is gunicorn, use environment variables for configuration
if [ "$1" = "gunicorn" ]; then
    PORT=${PORT:-8000}
    WEB_CONCURRENCY=${WEB_CONCURRENCY:-4}
    echo -e "${YELLOW}Starting Gunicorn on port ${PORT} with ${WEB_CONCURRENCY} workers${NC}"
    exec gunicorn config.wsgi:application \
        --bind "0.0.0.0:${PORT}" \
        --workers "${WEB_CONCURRENCY}" \
        --timeout 30 \
        --access-logfile - \
        --error-logfile -
else
    exec "$@"
fi
