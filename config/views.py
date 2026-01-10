"""
Core views for QuietPage.
"""

from django.conf import settings
from django.views.generic import TemplateView


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
