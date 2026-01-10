"""
QuietPage configuration package.

This module ensures the Celery app is loaded when Django starts,
enabling task autodiscovery and proper initialization.
"""

# Import Celery app to ensure it's loaded when Django starts
# This is required for Celery's autodiscover_tasks() to work properly
from .celery import app as celery_app

__all__ = ('celery_app',)
