"""
Journal models for QuietPage.

This module contains the Entry model with encryption support.
"""

import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from .fields import EncryptedTextField
from taggit.managers import TaggableManager


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
    tags = TaggableManager(blank=True)
    
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
    
    def save(self, *args, **kwargs):
        """Auto-calculate word count before saving."""
        # Calculate word count from content
        if self.content:
            self.word_count = len(self.content.split())
        else:
            self.word_count = 0
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('journal:entry-detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        date_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "Unsaved"
        title_preview = self.title[:30] if self.title else "Untitled"
        return f"{self.user.username} - {date_str} - {title_preview}"
