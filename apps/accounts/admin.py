"""
Django admin configuration for the User model.

This module configures how the custom User model is displayed and managed
in the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


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
