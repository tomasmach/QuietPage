"""
Base Django settings for QuietPage project.

This file contains settings that are common to all environments.
Environment-specific settings should be placed in development.py or production.py.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
# This should be overridden in development.py and production.py
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-please-change-this-in-env-file')

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

# WhiteNoise configuration for efficient static file serving
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
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
        'FERNET_KEY_PRIMARY environment variable is required. '
        'Generate a key with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
    )

# Django Taggit Configuration
TAGGIT_CASE_INSENSITIVE = True
TAGGIT_STRIP_UNICODE_WHEN_SLUGIFYING = False  # Support Czech characters

# Django AllAuth Configuration
AUTHENTICATION_BACKENDS = [
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
