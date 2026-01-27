"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from apps.api.views import HealthCheckView

# Admin URL obfuscation - use environment variable in production
# Security: Using a non-standard admin URL makes it harder for attackers to find the admin panel
# Example: ADMIN_URL=secret-dashboard-xyz/ in production environment
ADMIN_URL = os.getenv('ADMIN_URL', 'admin/')

# Prepare admin URL pattern for catch-all exclusion (escape special regex chars)
import re
admin_pattern = re.escape(ADMIN_URL)

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    # Health check endpoint (unauthenticated, for monitoring)
    path('api/health/', HealthCheckView.as_view(), name='health-check'),
    # API v1 routes
    path('api/v1/', include('apps.api.urls', namespace='api')),
    # OAuth routes (django-allauth)
    path('api/v1/auth/social/', include('allauth.socialaccount.urls')),
    # Google OAuth provider routes (login, callback)
    path('api/v1/auth/social/', include('allauth.socialaccount.providers.google.urls')),
    # SEO files - must be served from root URL for search engines
    path('sitemap.xml', views.SitemapView.as_view(), name='sitemap'),
    path('robots.txt', views.RobotsView.as_view(), name='robots'),
    # Catch-all pattern for React SPA - MUST be last
    # Excludes: API routes, admin panel (with or without trailing slash), debug toolbar, and static files
    # Serves React app on root and all other routes
    re_path(rf'^(?!api/|static/|{admin_pattern.rstrip("/")}(?:/|$)|__debug__/).*$', views.SPAView.as_view(), name='spa'),
]

# Django Debug Toolbar URLs (only in development)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        # debug_toolbar not installed (e.g., in Docker with production deps)
        pass
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
