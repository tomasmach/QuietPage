#!/bin/sh
# Docker entrypoint script for QuietPage
# Handles database migrations and static file collection before starting the application
# Note: Uses /bin/sh for compatibility with slim Docker images that don't have bash

set -e  # Exit on error

echo "=== QuietPage Docker Entrypoint ==="
echo "Environment: DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}"
echo "Environment: PORT=${PORT:-8000}"
echo "Environment: WEB_CONCURRENCY=${WEB_CONCURRENCY:-4}"

# Substitute environment variables in nginx config if they exist
if [ -n "$SSL_CERT_PATH" ] && [ -n "$SSL_KEY_PATH" ]; then
    echo "Substituting SSL certificate paths in nginx configuration..."
    if [ -f /etc/nginx/conf.d/quietpage.conf.template ]; then
        envsubst '$SSL_CERT_PATH $SSL_KEY_PATH' < /etc/nginx/conf.d/quietpage.conf.template > /etc/nginx/conf.d/quietpage.conf
        echo "SSL paths configured: $SSL_CERT_PATH"
    fi
elif [ -f /etc/nginx/conf.d/quietpage.conf.template ]; then
    echo "WARNING: SSL_CERT_PATH and SSL_KEY_PATH not set. Using template as-is."
    cp /etc/nginx/conf.d/quietpage.conf.template /etc/nginx/conf.d/quietpage.conf
fi

# Check if this is the web service (not celery worker/beat)
# We only want to run migrations and collectstatic for the web service
if [ "${DJANGO_SERVICE}" = "web" ] || [ "$1" = "gunicorn" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput

    echo "Collecting static files..."
    python manage.py collectstatic --noinput --clear

    echo "Setup complete!"
fi

# Execute the main command (gunicorn, celery, etc.)
echo "Starting: $*"

# If no command provided, determine based on DJANGO_SERVICE
if [ $# -eq 0 ] || [ "$1" = "gunicorn" ]; then
    # Check DJANGO_SERVICE environment variable
    case "${DJANGO_SERVICE}" in
        celery-worker)
            echo "Starting Celery Worker..."
            exec celery -A config worker -l info
            ;;
        celery-beat)
            echo "Starting Celery Beat..."
            exec celery -A config beat -l info
            ;;
        web|*)
            # Default to Gunicorn for web service
            PORT="${PORT:-8000}"
            WEB_CONCURRENCY="${WEB_CONCURRENCY:-4}"
            echo "Starting Gunicorn on port ${PORT} with ${WEB_CONCURRENCY} workers"
            exec gunicorn config.wsgi:application --config gunicorn.conf.py
            ;;
    esac
else
    exec "$@"
fi
