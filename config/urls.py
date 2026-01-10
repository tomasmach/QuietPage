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
from . import views  # type: ignore

# Admin URL obfuscation - use environment variable in production
# Security: Using a non-standard admin URL makes it harder for attackers to find the admin panel
# Example: ADMIN_URL=secret-dashboard-xyz/ in production environment
ADMIN_URL = os.getenv('ADMIN_URL', 'admin/')

# Prepare admin URL for regex pattern (strip trailing slash and escape special chars)
import re
admin_pattern = re.escape(ADMIN_URL.rstrip('/'))

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path('api/v1/', include('apps.api.urls', namespace='api')),
    # Catch-all pattern for React SPA - MUST be last
    # Serves React app on root and all other non-API/admin routes
    re_path(rf'^(?!api/|{admin_pattern}).*$', views.SPAView.as_view(), name='spa'),
]

# Django Debug Toolbar URLs (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
