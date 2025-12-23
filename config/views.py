"""
Core views for QuietPage.
"""

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    Homepage view - Landing page for QuietPage.
    
    Shows welcome message and CTA buttons for new/returning users.
    """
    template_name = 'home.html'
