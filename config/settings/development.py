"""
Development settings for QuietPage project.

These settings are optimized for local development.
- SQLite database
- DEBUG mode enabled
- Django Debug Toolbar enabled
- Relaxed security settings
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Django Debug Toolbar
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# Debug Toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Disable HTTPS redirect for development
SECURE_SSL_REDIRECT = False

# Session and CSRF settings for development (relaxed)
SESSION_COOKIE_SECURE = False  # Allow HTTP in development
CSRF_COOKIE_SECURE = False     # Allow HTTP in development

# Email backend - print emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
