"""
URL configuration for accounts app.

Settings URLs for user profile, goals, privacy, and security management.
"""

from django.urls import path
from django.views.generic import RedirectView
from . import views
from .views import AccountDeleteView

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

    # Security settings
    path('settings/security/password/',
         views.CustomPasswordChangeView.as_view(),
         name='settings-password'),
    path('settings/security/email/',
         views.EmailChangeView.as_view(),
         name='settings-email'),
    path('settings/security/email/verify/<str:token>/', views.EmailVerifyView.as_view(), name='email-verify'),
    path('settings/security/email/resend/', views.EmailResendVerificationView.as_view(), name='email-resend'),
    path('settings/security/email/cancel/', views.EmailCancelChangeView.as_view(), name='email-cancel'),

    # Account deletion
    path('settings/delete/',
          AccountDeleteView.as_view(),
          name='settings-delete'),
]
