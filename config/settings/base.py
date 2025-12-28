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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'taggit',
    'axes',  # Brute force protection

    # Local apps
    'apps.accounts',
    'apps.journal',
]

# Sites framework (required by allauth)
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # i18n support
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',  # MUST be after AuthenticationMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required by django-allauth
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
STATICFILES_DIRS = [BASE_DIR / 'static']  # Custom static files

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

# Caching Configuration (Database-backed - no Redis required)
# https://docs.djangoproject.com/en/5.2/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # Limit cache size
            'CULL_FREQUENCY': 3,  # Delete 1/3 of entries when MAX_ENTRIES is reached
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

# Django AllAuth Configuration
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # MUST be first for rate limiting
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Dual login: username OR email (modern django-allauth syntax)
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # MVP: optional, later: mandatory

# Custom forms for allauth
ACCOUNT_FORMS = {
    'signup': 'apps.accounts.forms.CustomSignupForm',
    'login': 'apps.accounts.forms.CustomLoginForm',
}

# Login/Logout URLs
LOGIN_REDIRECT_URL = '/journal/'  # Dashboard je na /journal/ (ne /journal/dashboard/)
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Session Configuration - "Remember me" automaticky (14 dní)
SESSION_COOKIE_AGE = 1209600  # 14 days in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Prodlouží session při každé aktivitě
SESSION_COOKIE_NAME = 'quietpage_sessionid'

# Django Axes - Brute Force Protection Configuration
# https://django-axes.readthedocs.io/
AXES_FAILURE_LIMIT = 5  # Lock after 5 failed login attempts
AXES_COOLOFF_TIME = timedelta(minutes=15)  # 15-minute lockout period
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]  # Lock by user+IP combination (nested list!)
AXES_RESET_ON_SUCCESS = True  # Reset failure counter on successful login
AXES_LOCKOUT_TEMPLATE = None  # Use default lockout response (403 Forbidden)
AXES_VERBOSE = True  # Log lockout events for debugging
