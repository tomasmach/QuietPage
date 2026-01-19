"""
Custom User model for QuietPage.

This module defines the custom User model that extends Django's AbstractUser.
It includes additional fields specific to the QuietPage application such as
timezone support for accurate date/time display and privacy settings.
"""

import uuid
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


class PasswordResetToken(models.Model):
    """
    Model for password reset tokens.

    When a user requests a password reset, a token is generated and stored here.
    The token is sent via email and can be used once within the expiration window.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        help_text="User requesting the password reset"
    )

    token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique token for password reset"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the reset was requested"
    )

    expires_at = models.DateTimeField(
        help_text="When this token expires (default: 1 hour)"
    )

    is_used = models.BooleanField(
        default=False,
        help_text="Whether the token has been used"
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the token was used"
    )

    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'is_used', 'expires_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        """Set expiry time on creation if not provided."""
        if not self.pk and not self.expires_at:
            # Default expiration: 1 hour from now
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if this token is valid (not expired and not used)."""
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True

    def mark_as_used(self):
        """Mark this token as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])

    def __str__(self):
        status = "used" if self.is_used else "active"
        return f"{self.user.username} - {status} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class EncryptionKey(models.Model):
    """
    Per-user encryption key for journal entry content.

    Each user has their own Fernet key for encrypting their journal entries.
    The key itself is encrypted with the global master key before storage,
    providing defense-in-depth security.

    Key rotation support: version field tracks which key version encrypted
    each entry, allowing gradual re-encryption when keys are rotated.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='encryption_key',
        help_text="User this encryption key belongs to"
    )
    key = models.CharField(
        max_length=500,
        help_text="Fernet key (encrypted with master key)"
    )
    version = models.IntegerField(
        default=1,
        help_text="Key version for rotation tracking"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this is the active key for new encryptions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    rotated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this key was last rotated"
    )

    class Meta:
        verbose_name = 'Encryption Key'
        verbose_name_plural = 'Encryption Keys'

    def save(self, *args, **kwargs):
        """Generate and encrypt key on first save."""
        if not self.key:
            # Generate new Fernet key
            from cryptography.fernet import Fernet
            from apps.journal.fields import get_fernet_key
            raw_key = Fernet.generate_key()
            # Encrypt it with master key before storage
            master_fernet = Fernet(get_fernet_key())
            self.key = master_fernet.encrypt(raw_key).decode('utf-8')
        super().save(*args, **kwargs)

    def get_decrypted_key(self):
        """
        Decrypt and return the raw Fernet key.

        Returns:
            bytes: The decrypted Fernet key ready for use
        """
        from cryptography.fernet import Fernet
        from apps.journal.fields import get_fernet_key
        master_fernet = Fernet(get_fernet_key())
        return master_fernet.decrypt(self.key.encode('utf-8'))

    def __str__(self):
        return f"EncryptionKey for {self.user.username} (v{self.version})"
