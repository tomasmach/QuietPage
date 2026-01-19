"""Tests for password reset views."""

import pytest
import contextlib
import copy
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.throttling import SimpleRateThrottle
from apps.accounts.models import PasswordResetToken
from apps.accounts.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordResetRequestView:
    """Test password reset request endpoint."""

    def test_request_reset_with_valid_email(self, client):
        """Test requesting password reset with valid email."""
        user = UserFactory(email='test@example.com')
        url = reverse('api:password-reset-request')

        with patch('apps.api.password_reset_views.send_password_reset_email_async.delay') as mock_task:
            response = client.post(url, {
                'email': 'test@example.com'
            }, content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.json()

        # Verify token was created
        assert PasswordResetToken.objects.filter(user=user).exists()

        # Verify email task was called
        mock_task.assert_called_once()

    def test_request_reset_with_nonexistent_email(self, client):
        """Test requesting reset with nonexistent email (should succeed for security)."""
        url = reverse('api:password-reset-request')

        response = client.post(url, {
            'email': 'nonexistent@example.com'
        }, content_type='application/json')

        # Should return success to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.json()

    def test_request_reset_with_invalid_email(self, client):
        """Test requesting reset with invalid email format."""
        url = reverse('api:password-reset-request')

        response = client.post(url, {
            'email': 'not-an-email'
        }, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.fixture
    def with_password_reset_rate_limit(self, settings):
        """Apply a specific rate limit for password reset endpoint within a test."""

        @contextlib.contextmanager
        def _apply_rate_limit(rate):
            # Deep copy current REST_FRAMEWORK settings
            rf_settings = copy.deepcopy(settings.REST_FRAMEWORK)
            rf_settings.setdefault("DEFAULT_THROTTLE_RATES", {})
            rf_settings["DEFAULT_THROTTLE_RATES"]["password_reset"] = rate

            # Apply settings override and patch throttle rates so DRF sees the change
            with override_settings(REST_FRAMEWORK=rf_settings):
                with patch.object(
                    SimpleRateThrottle,
                    "THROTTLE_RATES",
                    rf_settings["DEFAULT_THROTTLE_RATES"],
                ):
                    cache.clear()
                    yield

        return _apply_rate_limit

    @pytest.mark.rate_limiting
    def test_request_reset_rate_limiting(self, client, with_password_reset_rate_limit):
        """Test rate limiting on password reset requests."""
        user = UserFactory(email='test@example.com')
        url = reverse('api:password-reset-request')

        with with_password_reset_rate_limit('5/hour'):
            # Make multiple requests
            for i in range(6):
                response = client.post(url, {
                    'email': 'test@example.com'
                }, content_type='application/json')

                if i < 5:
                    assert response.status_code == status.HTTP_200_OK
                else:
                    # 6th request should be throttled
                    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordResetConfirmView:
    """Test password reset confirmation endpoint."""

    def test_confirm_reset_with_valid_token(self, client):
        """Test confirming password reset with valid token."""
        user = UserFactory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='valid_test_token'
        )

        url = reverse('api:password-reset-confirm')
        response = client.post(url, {
            'token': 'valid_test_token',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }, content_type='application/json')

        assert response.status_code == status.HTTP_200_OK

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password('NewSecurePass123!')

        # Verify token was marked as used
        token.refresh_from_db()
        assert token.is_used is True

    def test_confirm_reset_with_invalid_token(self, client):
        """Test confirming reset with invalid token."""
        url = reverse('api:password-reset-confirm')
        response = client.post(url, {
            'token': 'invalid_token',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()

    def test_confirm_reset_with_expired_token(self, client):
        """Test confirming reset with expired token."""
        from django.utils import timezone
        from datetime import timedelta

        user = UserFactory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='expired_token',
            expires_at=timezone.now() - timedelta(hours=1)
        )

        url = reverse('api:password-reset-confirm')
        response = client.post(url, {
            'token': 'expired_token',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_with_used_token(self, client):
        """Test confirming reset with already used token."""
        user = UserFactory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='used_token',
            is_used=True
        )

        url = reverse('api:password-reset-confirm')
        response = client.post(url, {
            'token': 'used_token',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        }, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_with_weak_password(self, client):
        """Test confirming reset with weak password."""
        user = UserFactory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='valid_token'
        )

        url = reverse('api:password-reset-confirm')
        response = client.post(url, {
            'token': 'valid_token',
            'new_password': '123',
            'new_password_confirm': '123'
        }, content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
