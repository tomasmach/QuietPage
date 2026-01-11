"""
Core app configuration for QuietPage.

This app contains infrastructure-level tasks and utilities that don't
belong to specific business logic (accounts, journal, etc.).

Includes:
- Database backup tasks
- Health check monitoring
- System maintenance tasks
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core Infrastructure'
