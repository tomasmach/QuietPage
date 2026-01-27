"""Tests for custom social account adapter."""

import pytest
from unittest.mock import Mock, patch
from django.test import RequestFactory
from apps.accounts.adapters import CustomSocialAccountAdapter
from apps.accounts.models import User


@pytest.mark.django_db
class TestCustomSocialAccountAdapter:
    """Tests for CustomSocialAccountAdapter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = CustomSocialAccountAdapter()
        self.factory = RequestFactory()

    def test_get_login_redirect_url_onboarding_not_completed(self):
        """User who hasn't completed onboarding goes to /onboarding."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            onboarding_completed=False,
        )
        request = self.factory.get('/')
        request.user = user

        url = self.adapter.get_login_redirect_url(request)

        assert '/onboarding' in url

    def test_get_login_redirect_url_onboarding_completed(self):
        """User who completed onboarding goes to /dashboard."""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            onboarding_completed=True,
        )
        request = self.factory.get('/')
        request.user = user

        url = self.adapter.get_login_redirect_url(request)

        assert '/dashboard' in url

    def test_generate_unique_username_simple(self):
        """Generate username from clean email prefix."""
        username = self.adapter._generate_unique_username('john')
        assert username == 'john'

    def test_generate_unique_username_with_special_chars(self):
        """Special characters are removed from username."""
        username = self.adapter._generate_unique_username('john+test@')
        assert username == 'johntest'

    def test_generate_unique_username_collision(self):
        """Numeric suffix added when username exists."""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123',
        )

        username = self.adapter._generate_unique_username('existinguser')

        assert username == 'existinguser1'

    def test_generate_unique_username_multiple_collisions(self):
        """Multiple numeric suffixes handled correctly."""
        User.objects.create_user(
            username='popular',
            email='popular@example.com',
            password='testpass123',
        )
        User.objects.create_user(
            username='popular1',
            email='popular1@example.com',
            password='testpass123',
        )

        username = self.adapter._generate_unique_username('popular')

        assert username == 'popular2'

    def test_generate_unique_username_empty_base(self):
        """Empty base defaults to 'user'."""
        username = self.adapter._generate_unique_username('')
        assert username == 'user'

    def test_generate_unique_username_truncates_long_base(self):
        """Long usernames are truncated to 20 chars."""
        long_name = 'a' * 50
        username = self.adapter._generate_unique_username(long_name)
        assert len(username) <= 20

    def test_populate_user_generates_username_from_email(self):
        """populate_user generates username from email and sets user attributes."""
        request = self.factory.get('/')
        sociallogin = Mock()
        data = {
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }

        user = self.adapter.populate_user(request, sociallogin, data)

        assert user.username == 'john.doe'
        assert user.email == 'john.doe@example.com'
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
