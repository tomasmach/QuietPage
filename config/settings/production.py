"""
Production settings for QuietPage project.

These settings are optimized for production deployment.
- PostgreSQL database
- DEBUG mode disabled
- Enhanced security settings
- All sensitive data from environment variables
"""

import os

from .base import *
from django.core.exceptions import ImproperlyConfigured
from csp.constants import SELF, NONE

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Add CSP middleware (Content Security Policy)
MIDDLEWARE += ['csp.middleware.CSPMiddleware']

# Parse ALLOWED_HOSTS from environment variable (comma-separated)
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        'ALLOWED_HOSTS must be set in production.\n'
        'Example: export ALLOWED_HOSTS="example.com,www.example.com"'
    )

# Database - PostgreSQL for production
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Security Settings
# https://docs.djangoproject.com/en/5.2/topics/security/

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY must be False for React SPA - JavaScript needs to read
# the CSRF token from the cookie to include it in API request headers
CSRF_COOKIE_HTTPONLY = False

# Session and CSRF cookie security (defense in depth)
SESSION_COOKIE_HTTPONLY = True  # Prevent XSS access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
CSRF_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# CSRF trusted origins - required for Django 4.0+ when using HTTPS
# Parse from environment variable, or derive from ALLOWED_HOSTS with https:// prefix
_csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '').strip()
if _csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_origins_env.split(',') if origin.strip()]
else:
    # Fallback: derive from ALLOWED_HOSTS with https:// prefix
    CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS]

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Referrer policy
SECURE_REFERRER_POLICY = 'same-origin'

# Email configuration (configure based on your email provider)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@quietpage.com')

# Logging configuration
# Ensure logs directory exists
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Content Security Policy (CSP)
# https://django-csp.readthedocs.io/
# Note: 'unsafe-inline' is used temporarily for scripts and styles
# TODO: Refactor inline scripts/styles to use nonces or hashes for better security
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [SELF],
        "script-src": [SELF, "'unsafe-inline'"],  # TODO: Remove unsafe-inline, use nonces
        "style-src": [SELF, "'unsafe-inline'", "https://fonts.googleapis.com"],  # Google Fonts CSS
        "img-src": [SELF, "data:", "https:"],     # Allow data URIs and HTTPS images
        "font-src": [SELF, "https://fonts.gstatic.com"],  # Google Fonts files
        "connect-src": [SELF],
        "frame-ancestors": [NONE],                # Prevent clickjacking (more strict than X-Frame-Options)
        "base-uri": [SELF],                       # Prevent base tag injection attacks
        "form-action": [SELF],                    # Prevent form hijacking attacks
    },
}

# CORS Configuration for Production
# In production, React SPA is served from the same domain (not a separate origin),
# so CORS is not needed. These settings are here for completeness and safety.
CORS_ALLOW_ALL_ORIGINS = False  # Never allow all origins in production
CORS_ALLOW_CREDENTIALS = True   # Allow cookies/credentials for same-origin requests
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']
