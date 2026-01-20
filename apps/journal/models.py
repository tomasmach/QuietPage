"""
Journal models for QuietPage.

This module contains the Entry model with encryption support.
"""

import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
# Note: EncryptedTextField removed - using per-user encryption instead
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase, GenericUUIDTaggedItemBase


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    """
    Custom TaggedItem model that supports UUID primary keys.
    
    This is required because django-taggit's default TaggedItem uses
    integer primary keys, but Entry uses UUID.
    """
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class Entry(models.Model):
    """
    Journal entry with encryption and smart features.
    
    Privacy: Content is encrypted at rest using Fernet symmetric encryption.
    Smart features: Auto word count, mood tracking, tagging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journal_entries'
    )
    
    # Content fields
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional title for your entry"
    )
    content = models.TextField(
        blank=True,
        help_text="Your private journal entry (encrypted with user's key)"
    )
    
    # Smart features
    mood_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate your mood: 1 (low) to 5 (high)"
    )
    word_count = models.IntegerField(
        default=0,
        editable=False,
        help_text="Automatically calculated word count"
    )
    is_favorite = models.BooleanField(
        default=False,
        help_text="Mark entry as favorite"
    )

    # Encryption tracking
    key_version = models.IntegerField(
        null=True,
        blank=True,
        help_text="Version of user's encryption key used for this entry"
    )

    # Tagging (free-form via django-taggit)
    tags = TaggableManager(through=UUIDTaggedItem, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._needs_encryption = False
        self._plaintext_for_word_count = None

    def _encrypt_content(self, plaintext):
        """Encrypt content with user's encryption key."""
        if not plaintext:
            return plaintext
        from cryptography.fernet import Fernet
        from django.core.exceptions import RelatedObjectDoesNotExist
        try:
            encryption_key = self.user.encryption_key.get_decrypted_key()
        except RelatedObjectDoesNotExist as exc:
            raise RuntimeError(
                f"No encryption key found for user {self.user.id}. "
                f"Please create an EncryptionKey for this user."
            ) from exc
        fernet = Fernet(encryption_key)
        return fernet.encrypt(plaintext.encode('utf-8')).decode('utf-8')

    def _decrypt_content(self, ciphertext):
        """Decrypt content with user's encryption key."""
        if not ciphertext:
            return ciphertext
        from cryptography.fernet import Fernet
        from django.core.exceptions import RelatedObjectDoesNotExist
        try:
            encryption_key = self.user.encryption_key.get_decrypted_key()
        except RelatedObjectDoesNotExist as exc:
            raise RuntimeError(
                f"No encryption key found for user {self.user.id}. "
                f"Please create an EncryptionKey for this user."
            ) from exc
        fernet = Fernet(encryption_key)
        return fernet.decrypt(ciphertext.encode('utf-8')).decode('utf-8')

    def get_content(self):
        """Get decrypted content."""
        if not self.content:
            return self.content
        if self.key_version is not None:
            return self._decrypt_content(self.content)
        return self.content

    def set_content(self, plaintext):
        """Set content and mark for encryption on save."""
        self._plaintext_for_word_count = plaintext
        self._needs_encryption = True
        self.content = plaintext

    def clean(self):
        """
        Model-level validation (belt-and-suspenders approach).
        Validates data even when forms are bypassed (API, admin, shell).
        """
        super().clean()

        # Allow empty content for 750words.com style daily notes
        # Streak will only update when word_count > 0 (handled in signals)

        # Mood rating bounds (double-check validators)
        if self.mood_rating is not None:
            if not (1 <= self.mood_rating <= 5):
                raise ValidationError({'mood_rating': 'Hodnocení musí být mezi 1 a 5.'})

    def save(self, *args, **kwargs):
        """Auto-calculate word count, encrypt content, and run validation."""
        skip_validation = kwargs.pop('skip_validation', False)

        if not skip_validation:
            self.full_clean()

        # Calculate word count from plaintext content
        if self._needs_encryption and self._plaintext_for_word_count:
            self.word_count = max(0, len(self._plaintext_for_word_count.split()))
        elif self.content and self.key_version is None:
            # New content not via set_content (plaintext)
            self.word_count = max(0, len(self.content.split()))
        elif not self.content:
            self.word_count = 0

        # Encrypt if needed
        if self._needs_encryption and self.content:
            self.content = self._encrypt_content(self.content)
            self.key_version = self.user.encryption_key.version
            self._needs_encryption = False
            self._plaintext_for_word_count = None
        elif self.content and self.key_version is None and not self._needs_encryption:
            # Content was set directly (plaintext), encrypt it
            self.word_count = max(0, len(self.content.split()))
            self.content = self._encrypt_content(self.content)
            self.key_version = self.user.encryption_key.version

        super().save(*args, **kwargs)

    def __str__(self):
        date_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "Unsaved"
        title_preview = self.title[:30] if self.title else "Untitled"
        return f"{self.user.username} - {date_str} - {title_preview}"


class FeaturedEntry(models.Model):
    """
    Stores the randomly selected 'memory' entry shown on dashboard each day.

    Ensures same entry is shown across all devices for the same user on the same day.
    Date is stored in user's timezone to handle midnight correctly.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='featured_entries'
    )
    date = models.DateField(
        help_text="Date in user's timezone when this entry was featured"
    )
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name='featured_appearances'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Featured Entry"
        verbose_name_plural = "Featured Entries"
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.entry_id}"