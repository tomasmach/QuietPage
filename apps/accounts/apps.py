"""
Django app configuration for the accounts app.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for the accounts application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'User Accounts'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures signals are registered at startup.
        """
        import apps.accounts.signals  # noqa: F401
