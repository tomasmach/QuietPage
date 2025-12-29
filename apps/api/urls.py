"""
URL configuration for QuietPage API.

This module defines the URL routing for the REST API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'api'

# Create a router for ViewSet-based endpoints
router = DefaultRouter()

# ViewSets will be registered here in the next phase:
# router.register(r'users', UserViewSet, basename='user')
# router.register(r'entries', EntryViewSet, basename='entry')

urlpatterns = [
    # Router URLs (ViewSets)
    path('', include(router.urls)),

    # Additional custom endpoints will be added here
    # Example: path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
