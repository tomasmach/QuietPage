"""
Django admin configuration for the User model.

This module configures how the custom User model is displayed and managed
in the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, EmailChangeRequest, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for User model.
    
    Extends Django's default UserAdmin to include additional fields
    specific to QuietPage (timezone, email_notifications).
    """
    
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'date_joined'
    ]
    
    list_filter = [
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
        'email_notifications'
    ]
    
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name'
    ]
    
    ordering = ['-date_joined']
    
    # Add custom fields to the fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('QuietPage Settings', {
            'fields': ('timezone', 'email_notifications')
        }),
        ('Writing Stats', {
            'fields': ('current_streak', 'longest_streak', 'last_entry_date'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    # Fields shown when creating a new user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'timezone')
        }),
    )
    
    # Make timestamp fields readonly
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')


@admin.register(EmailChangeRequest)
class EmailChangeRequestAdmin(admin.ModelAdmin):
    """
    Admin configuration for EmailChangeRequest model.
    
    Displays email change requests with filtering and search capabilities.
    """
    
    list_display = [
        'user',
        'new_email',
        'created_at',
        'expires_at',
        'is_verified',
        'verified_at'
    ]
    
    list_filter = [
        'is_verified',
        'created_at',
        'expires_at'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'new_email'
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = [
        'user',
        'new_email',
        'created_at',
        'expires_at',
        'is_verified',
        'verified_at'
    ]
    
    def has_add_permission(self, request):
        """Disable adding email change requests via admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make all fields read-only."""
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin interface for password reset tokens."""

    list_display = ['user', 'created_at', 'expires_at', 'is_used', 'used_at']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'created_at', 'used_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Token Details', {
            'fields': ('token', 'created_at', 'expires_at')
        }),
        ('Status', {
            'fields': ('is_used', 'used_at')
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation of tokens."""
        return False
