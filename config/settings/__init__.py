"""
Django settings package for QuietPage project.

Use environment variable DJANGO_SETTINGS_MODULE to specify which settings to use:
- config.settings.development (default for local development)
- config.settings.production (for production deployment)

Alternatively, set DJANGO_ENV environment variable to 'production' or 'development'.
"""

import os

# Determine which settings to use based on DJANGO_ENV environment variable
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
else:
    from .development import *
