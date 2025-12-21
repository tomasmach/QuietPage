"""
Custom User model for QuietPage.

This module defines the custom User model that extends Django's AbstractUser.
It includes additional fields specific to the QuietPage application such as
timezone support for accurate date/time display and privacy settings.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from timezone_field import TimeZoneField


class User(AbstractUser):
    """
    Custom User model for QuietPage.
    
    Uses both username and email for flexibility.
    Username is the primary login field, email is required and unique.
    
    Additional Features:
    - Timezone support for accurate date/time display
    - Email notifications opt-in for privacy
    - Timestamps for account creation and updates
    """
    
    email = models.EmailField(
        unique=True,
        verbose_name="Email address",
        help_text="Required. Enter a valid email address."
    )
    
    # Wellbeing-specific fields
    timezone = TimeZoneField(
        default='Europe/Prague',
        help_text="Your timezone for accurate date and time display"
    )
    
    # Privacy settings
    email_notifications = models.BooleanField(
        default=False,
        help_text="Opt-in for email notifications"
    )
    
    # Writing streak tracking
    current_streak = models.IntegerField(
        default=0,
        help_text="Current consecutive days writing streak"
    )
    longest_streak = models.IntegerField(
        default=0,
        help_text="Longest writing streak achieved"
    )
    last_entry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last journal entry (in user timezone)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Keep username as primary login field (default Django behavior)
    # USERNAME_FIELD = 'username'  # Default, no need to specify
    REQUIRED_FIELDS = ['email']  # Email required for createsuperuser
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
