"""
Custom middleware for QuietPage.
"""

import os
from django.http import HttpResponsePermanentRedirect


class CanonicalDomainMiddleware:
    """
    Middleware to redirect to the canonical domain (www version).

    This ensures OAuth callbacks work correctly by always using the same domain
    that's configured in the Django Sites framework and Google Cloud Console.

    The canonical domain is read from CANONICAL_DOMAIN environment variable.
    If not set, no redirect is performed.

    Example:
        CANONICAL_DOMAIN=www.quietpage.app

    This will redirect:
        https://quietpage.app/any/path -> https://www.quietpage.app/any/path
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.canonical_domain = os.getenv('CANONICAL_DOMAIN', '').strip()

    def __call__(self, request):
        # Skip if no canonical domain configured
        if not self.canonical_domain:
            return self.get_response(request)

        # Get the current host (without port)
        host = request.get_host().split(':')[0]

        # If already on canonical domain, continue normally
        if host == self.canonical_domain:
            return self.get_response(request)

        # Build redirect URL to canonical domain
        scheme = 'https' if request.is_secure() else 'http'
        path = request.get_full_path()
        redirect_url = f'{scheme}://{self.canonical_domain}{path}'

        return HttpResponsePermanentRedirect(redirect_url)
