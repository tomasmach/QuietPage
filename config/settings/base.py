"""
Base Django settings for QuietPage project.

This file contains settings that are common to all environments.
Environment-specific settings should be placed in development.py or production.py.
"""

from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY must be set in environment variables - no fallback for security
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured(
        'SECRET_KEY environment variable is required.\n'
        'Generate with: python -c "import secrets; print(secrets.token_urlsafe(50))"'
    )

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth

    # Third-party
    'rest_framework',
    'corsheaders',
    'taggit',
    'axes',  # Brute force protection
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Local apps
    'apps.accounts',
    'apps.journal',
    'apps.api',
    'apps.core',  # Infrastructure tasks
]

# Django Sites Framework (required by allauth)
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS - must be before CommonMiddleware
    'django.middleware.locale.LocaleMiddleware',  # i18n support
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',  # MUST be after AuthenticationMiddleware
    'allauth.account.middleware.AccountMiddleware',  # After AuthenticationMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.api.context_processors.vite_assets',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'cs'  # Default language: Czech

# Supported languages
LANGUAGES = [
    ('cs', 'Čeština'),
    # ('en', 'English'),  # Ready for future translation
]

# Path to translation files
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For collectstatic

# Custom static files directories
_staticfiles_dirs = []

# Add Vite build output directory if it exists (for production)
_vite_dist = BASE_DIR / 'frontend' / 'dist'
if _vite_dist.exists():
    _staticfiles_dirs.append(_vite_dist)

STATICFILES_DIRS = _staticfiles_dirs

# Media files (User uploaded files - avatars, etc.)
# https://docs.djangoproject.com/en/5.2/topics/files/
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise configuration for efficient static file serving
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Redis URL for caching and health checks
# Used by Celery broker, cache backend, and health check task
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

# Caching Configuration (Redis-backed for production performance)
# https://docs.djangoproject.com/en/5.2/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
            },
        }
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
# CRITICAL: This must be set before running the first migration
AUTH_USER_MODEL = 'accounts.User'

# Field Encryption for Journal Entries
# CRITICAL: Must be set in environment variables for security
FIELD_ENCRYPTION_KEY = os.getenv('FERNET_KEY_PRIMARY')
if not FIELD_ENCRYPTION_KEY:
    raise ImproperlyConfigured(
        'FERNET_KEY_PRIMARY environment variable is required.\n'
        'Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
    )

# Validate encryption key format and length
if isinstance(FIELD_ENCRYPTION_KEY, str):
    FIELD_ENCRYPTION_KEY = FIELD_ENCRYPTION_KEY.encode('utf-8')

# Must be exactly 44 bytes (32 bytes base64-encoded)
if len(FIELD_ENCRYPTION_KEY) != 44:
    raise ImproperlyConfigured(
        f'FERNET_KEY_PRIMARY must be 44 bytes (got {len(FIELD_ENCRYPTION_KEY)}).\n'
        'Ensure you copied the entire base64-encoded key.'
    )

# Validate it's a valid Fernet key
try:
    from cryptography.fernet import Fernet
    Fernet(FIELD_ENCRYPTION_KEY)
except Exception as e:
    raise ImproperlyConfigured(f'Invalid FERNET_KEY_PRIMARY: {e}')

# Django Taggit Configuration
TAGGIT_CASE_INSENSITIVE = True
TAGGIT_STRIP_UNICODE_WHEN_SLUGIFYING = False  # Support Czech characters

# Authentication Configuration
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # MUST be first for rate limiting
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Session security - zkrácený timeout s automatickou prolongací při aktivitě
# Bezpečnostní důvody:
# - 2 hodiny minimalizují riziko zneužití opuštěné session (např. na veřejném PC)
# - SESSION_SAVE_EVERY_REQUEST = sliding window - aktivní uživatelé nejsou odhlášeni
# - Vyvážený kompromis mezi bezpečností a UX (journaling vyžaduje delší session než banking)
SESSION_COOKIE_AGE = 7200  # 2 hodiny (kompromis mezi bezpečností a UX)
SESSION_SAVE_EVERY_REQUEST = True  # Sliding window - session se prodlužuje při každém requestu
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Zachovat session i po zavření prohlížeče
SESSION_COOKIE_NAME = 'quietpage_sessionid'

# Django Axes - Brute Force Protection Configuration
# https://django-axes.readthedocs.io/
AXES_FAILURE_LIMIT = 5  # Lock after 5 failed login attempts
AXES_COOLOFF_TIME = timedelta(minutes=15)  # 15-minute lockout period
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]  # Lock by user+IP combination (nested list!)
AXES_RESET_ON_SUCCESS = True  # Reset failure counter on successful login
AXES_LOCKOUT_TEMPLATE = None  # Use default lockout response (403 Forbidden)
AXES_VERBOSE = True  # Log lockout events for debugging
AXES_HANDLER = 'axes.handlers.cache.AxesCacheHandler'  # Use Redis cache instead of DB

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'register': '5/hour',
        'entries_create': '100/day',
        'avatar_upload': '10/hour',
        'statistics': '100/hour',  # Expensive queries - limit to prevent database exhaustion
        'export_download': '5/hour',  # Limit export downloads to prevent abuse
        'password_reset': '5/hour',  # Limit password reset requests to prevent abuse
        'email_change': '3/hour',
    },
}

# ============================================
# CELERY CONFIGURATION
# ============================================
# https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html

# Broker and Backend
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Task Serialization
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_TRACK_STARTED = True

# Task Limits
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit

# Timezone
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Result Backend
CELERY_RESULT_EXPIRES = 3600  # 1 hour
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10

# Execution Settings
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Retry Policy
CELERY_TASK_DEFAULT_RETRY_DELAY = 60
CELERY_TASK_MAX_RETRIES = 3

# Beat Schedule (Periodic Tasks)
# Using file-based scheduler (celerybeat-schedule) until django-celery-beat supports Django 6.0
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-email-requests-daily': {
        'task': 'apps.journal.tasks.cleanup_expired_email_requests',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
        'options': {'expires': 3600},
    },
    'weekly-cleanup': {
        'task': 'apps.journal.tasks.weekly_cleanup',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3:00 AM
        'options': {'expires': 7200},
    },
    'database-backup-daily': {
        'task': 'apps.core.tasks.database_backup',
        'schedule': crontab(hour=1, minute=0),  # 1:00 AM daily
        'options': {'expires': 3600},
    },
    'cleanup-old-backups-weekly': {
        'task': 'apps.core.tasks.cleanup_old_backups',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),  # Sunday 4:00 AM
        'options': {'expires': 3600},
    },
    'health-check-hourly': {
        'task': 'apps.core.tasks.health_check',
        'schedule': crontab(minute=0),  # Every hour
        'options': {'expires': 300},
    },
    'send-writing-reminders-daily': {
        'task': 'apps.accounts.tasks.send_reminder_emails',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
        'options': {'expires': 3600},
    },
}

# Logging
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

# Site URL for absolute URL generation in emails
SITE_URL = os.getenv('SITE_URL', 'http://localhost:5173')

# ============================================
# EMAIL CONFIGURATION
# ============================================
# Email backend (Resend for production, console for development)
EMAIL_BACKEND = 'apps.core.backends.resend_backend.ResendEmailBackend'

# Resend API configuration
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
if not RESEND_API_KEY:
    raise ImproperlyConfigured(
        'RESEND_API_KEY environment variable is required.\n'
        'Get your API key from: https://resend.com/api-keys'
    )

# Email sender configuration
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'info@quietpage.app')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ============================================
# BACKUPS CONFIGURATION
# ============================================
# Directory for database backups
# In production, this should be a persistent volume mounted path
# Default to BASE_DIR/backups for development
BACKUPS_DIR = Path(os.getenv('BACKUPS_PATH', str(BASE_DIR / 'backups')))

# ============================================
# GOOGLE OAUTH CONFIGURATION (django-allauth)
# ============================================

# Frontend URL for OAuth redirects
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Allauth base settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Google email already verified

# Social account settings
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True  # Enable account linking by email
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True  # Auto-connect on email match

# Custom adapter for redirect handling
SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomSocialAccountAdapter'

# Google OAuth provider settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
        },
    }
}
