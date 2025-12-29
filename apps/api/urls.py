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

    # Autosave endpoint (must come before router URLs to avoid conflicts)
    path('entries/autosave/', AutosaveView.as_view(), name='entry-autosave'),

    # Router URLs (ViewSets) - must come last to avoid URL conflicts
    path('', include(router.urls)),
]
