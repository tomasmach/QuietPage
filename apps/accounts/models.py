"""
Custom User model for QuietPage.

This module defines the custom User model that extends Django's AbstractUser.
It includes additional fields specific to the QuietPage application such as
timezone support for accurate date/time display and privacy settings.
"""

from datetime import time, timedelta
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
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
    
    # Profile fields
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        help_text="Profile picture (max 2MB, 512x512px recommended)"
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Short bio about yourself"
    )
    
    # Writing goals and preferences
    daily_word_goal = models.IntegerField(
        default=750,
        validators=[MinValueValidator(100), MaxValueValidator(5000)],
        help_text="Daily word count goal (100-5000 words)"
    )
    preferred_writing_time = models.CharField(
        max_length=20,
        choices=[
            ('morning', 'Ráno (do 12:00)'),
            ('afternoon', 'Odpoledne (12:00-18:00)'),
            ('evening', 'Večer (18:00+)'),
            ('anytime', 'Kdykoli'),
        ],
        default='morning',
        help_text="Preferred time of day for writing"
    )
    reminder_enabled = models.BooleanField(
        default=False,
        help_text="Enable daily writing reminders"
    )
    reminder_time = models.TimeField(
        default=time(8, 0),
        help_text="Time for daily reminder"
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
        help_text="Date of last journal entry (in user timezone)",
        db_index=True
    )

    # Language and theme preferences
    preferred_language = models.CharField(
        max_length=2,
        choices=[('cs', 'Čeština'), ('en', 'English')],
        default='cs',
        verbose_name='Preferovaný jazyk',
        help_text="User's preferred language"
    )
    preferred_theme = models.CharField(
        max_length=10,
        choices=[('midnight', 'Midnight'), ('paper', 'Paper')],
        default='midnight',
        verbose_name='Preferovaný motiv',
        help_text="User's preferred theme"
    )

    # Onboarding
    onboarding_completed = models.BooleanField(
        default=False,
        help_text="Whether user has completed the onboarding process"
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


class EmailChangeRequest(models.Model):
    """
    Model for tracking email change requests with verification.
    
    When a user requests to change their email, a record is created here.
    The user receives a verification link to confirm the new email address.
    Once verified, the user's email is updated and this record is marked as verified.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_change_requests',
        help_text="User requesting the email change"
    )
    
    new_email = models.EmailField(
        verbose_name="New email address",
        help_text="The email address user wants to change to"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the change was requested"
    )
    
    expires_at = models.DateTimeField(
        help_text="When this request expires (default: 24 hours)"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the email has been verified"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the email was verified"
    )
    
    class Meta:
        verbose_name = 'Email Change Request'
        verbose_name_plural = 'Email Change Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['new_email', 'is_verified']),
            models.Index(fields=['user', 'is_verified', '-created_at']),
            models.Index(fields=['is_verified', 'expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Set expiry time on creation if not provided."""
        if not self.pk and not self.expires_at:
            # Default expiration: 24 hours from now
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if this request has expired."""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        status = "verified" if self.is_verified else "pending"
        return f"{self.user.username} → {self.new_email} ({status})"
