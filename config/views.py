"""
Core views for QuietPage.
"""

from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View
from django.views.generic import TemplateView


class StaticFileView(View):
    """
    Serve static files from root URL (sitemap.xml, robots.txt).

    These files need to be served from the root URL path, not from /static/,
    so they can be discovered by search engines and crawlers.
    """

    filename: str = ''
    content_type: str = 'text/plain'

    def get(self, request, *args, **kwargs):
        # Try to find the file in staticfiles (production) or frontend directories
        search_paths = [
            Path(settings.STATIC_ROOT) / self.filename,
            settings.BASE_DIR / 'frontend' / 'dist' / self.filename,
            settings.BASE_DIR / 'frontend' / 'public' / self.filename,
        ]

        for file_path in search_paths:
            if file_path.is_file():
                return FileResponse(
                    open(file_path, 'rb'),
                    content_type=self.content_type,
                )

        raise Http404(f'{self.filename} not found')


class SitemapView(StaticFileView):
    """Serve sitemap.xml from root URL."""

    filename = 'sitemap.xml'
    content_type = 'application/xml'


class RobotsView(StaticFileView):
    """Serve robots.txt from root URL."""

    filename = 'robots.txt'
    content_type = 'text/plain'


class SPAView(TemplateView):
    """
    Single Page Application view for React frontend.

    Serves the SPA shell template that loads the React application.
    In development mode, assets are loaded from Vite dev server.
    In production mode, assets are loaded from the Vite manifest.
    """
    template_name = 'spa.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debug'] = settings.DEBUG
        return context
