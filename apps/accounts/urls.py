"""
URL configuration for accounts app.

Settings URLs for user profile, goals, privacy, and security management.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Settings overview (redirects to profile)
    path('settings/', views.SettingsOverviewView.as_view(), name='settings-overview'),
    
    # Profile settings
    path('settings/profile/', views.ProfileUpdateView.as_view(), name='settings-profile'),
    
    # Goals and preferences
    path('settings/goals/', views.GoalsUpdateView.as_view(), name='settings-goals'),
    
    # Privacy settings
    path('settings/privacy/', views.PrivacySettingsView.as_view(), name='settings-privacy'),
    
    # Security settings (will be implemented in Phase 10)
    # path('settings/security/password/', views.PasswordChangeView.as_view(), name='settings-password'),
    # path('settings/security/email/', views.EmailChangeView.as_view(), name='settings-email'),
    
    # Account deletion (will be implemented in Phase 10)
    # path('settings/delete/', views.AccountDeleteView.as_view(), name='settings-delete'),
]
