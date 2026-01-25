"""
Custom adapters for django-allauth social authentication.

Handles OAuth redirect logic and username generation for new OAuth users.
"""

import re
from django.conf import settings
from django.shortcuts import redirect
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account authentication.

    Handles:
    - Redirect URLs after successful OAuth login
    - Error redirects to frontend
    - Username generation for new OAuth users
    """

    def get_login_redirect_url(self, request):
        """Redirect to frontend after successful OAuth login."""
        user = request.user
        if not user.onboarding_completed:
            return f"{settings.FRONTEND_URL}/onboarding"
        return f"{settings.FRONTEND_URL}/dashboard"

    def authentication_error(
        self, request, provider_id, error=None, exception=None, extra_context=None
    ):
        """Redirect to frontend with error on OAuth failure."""
        return redirect(f"{settings.FRONTEND_URL}/login?error=oauth_failed")

    def populate_user(self, request, sociallogin, data):
        """Generate username for new OAuth users from email."""
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            email = data.get('email', '')
            base = email.split('@')[0] if email else 'user'
            user.username = self._generate_unique_username(base)
        return user

    def _generate_unique_username(self, base: str) -> str:
        """
        Generate a unique username from email prefix.

        Args:
            base: The email prefix to use as username base

        Returns:
            A unique username that doesn't exist in the database
        """
        from apps.accounts.models import User

        # Clean base: only alphanumeric, underscore, dot (max 20 chars)
        base = re.sub(r'[^a-zA-Z0-9_.]', '', base)[:20]
        if not base:
            base = 'user'

        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        return username
