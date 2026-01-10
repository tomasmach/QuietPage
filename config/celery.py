"""
Celery configuration for QuietPage project.

This module initializes the Celery application instance and configures
task discovery, serialization, timezone settings, and broker/backend connections.

Celery will automatically discover tasks from all installed Django apps
by looking for tasks.py modules in each app directory.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create Celery app instance
app = Celery('quietpage')

# Load configuration from Django settings with CELERY_ namespace
# This means all Celery config keys in settings.py should be prefixed with CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
# Celery will look for tasks.py in each app listed in INSTALLED_APPS
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Debug task to verify Celery is working correctly.

    Usage:
        from config.celery import debug_task
        debug_task.delay()
    """
    print(f'Request: {self.request!r}')
