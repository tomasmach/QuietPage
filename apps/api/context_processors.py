"""
Django context processors for the API app.

Provides template context variables for Vite asset integration.
"""

from django.http import HttpRequest

from .vite import get_vite_assets


def vite_assets(request: HttpRequest) -> dict:
    """
    Add Vite asset paths to template context.

    In development mode, returns empty lists (Vite dev server serves assets).
    In production mode, returns paths parsed from the Vite manifest.

    Args:
        request: The HTTP request object.

    Returns:
        Dictionary with 'vite_js' and 'vite_css' lists.
    """
    assets = get_vite_assets()
    return {
        'vite_js': assets['js'],
        'vite_css': assets['css'],
    }
