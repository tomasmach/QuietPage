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

app_name = 'api'

# Create a router for ViewSet-based endpoints
router = DefaultRouter()

# ViewSets will be registered here in the next phase:
# router.register(r'users', UserViewSet, basename='user')
# router.register(r'entries', EntryViewSet, basename='entry')

urlpatterns = [
    # Router URLs (ViewSets)
    path('', include(router.urls)),

    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/csrf/', CSRFTokenView.as_view(), name='csrf-token'),

    # Additional custom endpoints will be added here
    # Example: path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
