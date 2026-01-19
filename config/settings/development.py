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

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']

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
SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cross-origin requests with credentials

CSRF_COOKIE_SECURE = False     # Allow HTTP in development
CSRF_COOKIE_HTTPONLY = False   # CRITICAL: JavaScript needs to read CSRF token from cookie
CSRF_COOKIE_SAMESITE = 'Lax'   # Allow cross-origin requests with credentials
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# Email backend - print emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'QuietPage <noreply@quietpage.com>'

# CORS Configuration for Development (React frontend)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']

# Static files - Add frontend/public/ for development (favicons, og-image, etc.)
# In production, these files are copied to dist/ by Vite build
STATICFILES_DIRS = list(STATICFILES_DIRS) + [BASE_DIR / 'frontend' / 'public']

# Cache Configuration - Use local memory for development (no Redis needed)
# https://docs.djangoproject.com/en/5.2/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'quietpage-dev-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}
