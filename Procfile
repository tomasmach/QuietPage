web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-4} --timeout 30 --access-logfile - --error-logfile -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
