"""
Tests for custom middleware.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.http import HttpResponsePermanentRedirect

from apps.core.middleware import CanonicalDomainMiddleware


class TestCanonicalDomainMiddleware:
    """Tests for CanonicalDomainMiddleware."""

    def test_no_redirect_when_canonical_domain_not_set(self):
        """Should pass through when CANONICAL_DOMAIN is not set."""
        with patch.dict('os.environ', {'CANONICAL_DOMAIN': ''}):
            get_response = MagicMock(return_value='response')
            middleware = CanonicalDomainMiddleware(get_response)

            request = MagicMock()
            request.get_host.return_value = 'quietpage.app'

            result = middleware(request)

            assert result == 'response'
            get_response.assert_called_once_with(request)

    def test_no_redirect_when_already_on_canonical_domain(self):
        """Should pass through when already on canonical domain."""
        with patch.dict('os.environ', {'CANONICAL_DOMAIN': 'www.quietpage.app'}):
            get_response = MagicMock(return_value='response')
            middleware = CanonicalDomainMiddleware(get_response)

            request = MagicMock()
            request.get_host.return_value = 'www.quietpage.app'

            result = middleware(request)

            assert result == 'response'
            get_response.assert_called_once_with(request)

    def test_redirect_non_www_to_www(self):
        """Should redirect non-www to www domain."""
        with patch.dict('os.environ', {'CANONICAL_DOMAIN': 'www.quietpage.app'}):
            get_response = MagicMock()
            middleware = CanonicalDomainMiddleware(get_response)

            request = MagicMock()
            request.get_host.return_value = 'quietpage.app'
            request.is_secure.return_value = True
            request.get_full_path.return_value = '/dashboard/'

            result = middleware(request)

            assert isinstance(result, HttpResponsePermanentRedirect)
            assert result.url == 'https://www.quietpage.app/dashboard/'
            get_response.assert_not_called()

    def test_redirect_preserves_query_string(self):
        """Should preserve query string in redirect."""
        with patch.dict('os.environ', {'CANONICAL_DOMAIN': 'www.quietpage.app'}):
            get_response = MagicMock()
            middleware = CanonicalDomainMiddleware(get_response)

            request = MagicMock()
            request.get_host.return_value = 'quietpage.app'
            request.is_secure.return_value = True
            request.get_full_path.return_value = '/login/?next=/dashboard/'

            result = middleware(request)

            assert isinstance(result, HttpResponsePermanentRedirect)
            assert result.url == 'https://www.quietpage.app/login/?next=/dashboard/'

    def test_redirect_uses_http_when_not_secure(self):
        """Should use HTTP scheme when request is not secure."""
        with patch.dict('os.environ', {'CANONICAL_DOMAIN': 'www.quietpage.app'}):
            get_response = MagicMock()
            middleware = CanonicalDomainMiddleware(get_response)

            request = MagicMock()
            request.get_host.return_value = 'quietpage.app'
            request.is_secure.return_value = False
            request.get_full_path.return_value = '/'

            result = middleware(request)

            assert isinstance(result, HttpResponsePermanentRedirect)
            assert result.url == 'http://www.quietpage.app/'

    def test_redirect_handles_host_with_port(self):
        """Should handle host with port correctly."""
        with patch.dict('os.environ', {'CANONICAL_DOMAIN': 'www.quietpage.app'}):
            get_response = MagicMock()
            middleware = CanonicalDomainMiddleware(get_response)

            request = MagicMock()
            request.get_host.return_value = 'quietpage.app:8000'
            request.is_secure.return_value = True
            request.get_full_path.return_value = '/'

            result = middleware(request)

            assert isinstance(result, HttpResponsePermanentRedirect)
            assert result.url == 'https://www.quietpage.app/'
