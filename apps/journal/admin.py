"""
Django admin configuration for journal app.
"""

from django.contrib import admin
from .models import Entry


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    """Admin interface for journal entries."""
    
    list_display = ['user', 'title_preview', 'mood_rating', 'word_count', 'created_at']
    list_filter = ['mood_rating', 'created_at', 'user']
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = ['id', 'word_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('user', 'title', 'content')
        }),
        ('Metadata', {
            'fields': ('mood_rating', 'tags', 'word_count')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_preview(self, obj):
        """Show title preview or 'Untitled'."""
        return obj.title[:50] if obj.title else "(Untitled)"
    title_preview.short_description = "Title"
    
    def get_queryset(self, request):
        """
        Admin users see only their own entries (unless superuser).
        Privacy protection.
        """
        qs = super().get_queryset(request).select_related('user')
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
