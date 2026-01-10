"""
Journal models for QuietPage.

This module contains the Entry model with encryption support.
"""

import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .fields import EncryptedTextField
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
    content = EncryptedTextField(
        blank=True,
        help_text="Your private journal entry (encrypted)"
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
        """Auto-calculate word count and run validation before saving."""
        # Allow callers to skip validation for non-form contexts
        skip_validation = kwargs.pop('skip_validation', False)

        # Run full model validation (including clean()) unless explicitly skipped
        if not skip_validation:
            self.full_clean()

        # Calculate word count from content (ensure non-negative)
        if self.content:
            self.word_count = max(0, len(self.content.split()))
        else:
            self.word_count = 0

        super().save(*args, **kwargs)

    def __str__(self):
        date_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "Unsaved"
        title_preview = self.title[:30] if self.title else "Untitled"
        return f"{self.user.username} - {date_str} - {title_preview}"
