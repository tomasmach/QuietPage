"""
URL configuration for QuietPage API.

This module defines the URL routing for the REST API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.api.auth_views import (
    LoginView,
    LogoutView,
    RegisterView,
    CurrentUserView,
    CSRFTokenView,
)
from apps.api.views import (
    EntryViewSet,
    DashboardView,
    AutosaveView,
    TodayEntryView,
)
from apps.api.statistics_views import (
    StatisticsView,
)
from apps.api.settings_views import (
    ProfileSettingsView,
    GoalsSettingsView,
    PrivacySettingsView,
    ChangePasswordView,
    ChangeEmailView,
    DeleteAccountView,
)

app_name = 'api'

# Create a router for ViewSet-based endpoints
router = DefaultRouter()

# Register ViewSets
router.register(r'entries', EntryViewSet, basename='entry')

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/csrf/', CSRFTokenView.as_view(), name='csrf-token'),

    # Dashboard endpoint
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Statistics endpoint
    path('statistics/', StatisticsView.as_view(), name='statistics'),

    # Today's entry endpoint (must come before autosave and router URLs)
    path('entries/today/', TodayEntryView.as_view(), name='entry-today'),

    # Autosave endpoint (must come before router URLs to avoid conflicts)
    path('entries/autosave/', AutosaveView.as_view(), name='entry-autosave'),

    # Settings endpoints
    path('settings/profile/', ProfileSettingsView.as_view(), name='settings-profile'),
    path('settings/goals/', GoalsSettingsView.as_view(), name='settings-goals'),
    path('settings/privacy/', PrivacySettingsView.as_view(), name='settings-privacy'),
    path('settings/change-password/', ChangePasswordView.as_view(), name='settings-change-password'),
    path('settings/change-email/', ChangeEmailView.as_view(), name='settings-change-email'),
    path('settings/delete-account/', DeleteAccountView.as_view(), name='settings-delete-account'),

    # Router URLs (ViewSets) - must come last to avoid URL conflicts
    path('', include(router.urls)),
]
