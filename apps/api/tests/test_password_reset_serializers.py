"""Tests for password reset serializers."""

import pytest
from django.contrib.auth import get_user_model
from apps.api.password_reset_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from apps.accounts.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordResetRequestSerializer:
    """Test PasswordResetRequestSerializer."""

    def test_valid_email(self):
        """Test serializer with valid email."""
        user = UserFactory(email='test@example.com')

        serializer = PasswordResetRequestSerializer(
            data={'email': 'test@example.com'}
        )

        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'test@example.com'

    def test_email_required(self):
        """Test email field is required."""
        serializer = PasswordResetRequestSerializer(data={})

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_invalid_email_format(self):
        """Test invalid email format."""
        serializer = PasswordResetRequestSerializer(
            data={'email': 'not-an-email'}
        )

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_nonexistent_email_is_valid(self):
        """Test that nonexistent email passes validation (security)."""
        serializer = PasswordResetRequestSerializer(
            data={'email': 'nonexistent@example.com'}
        )

        # Should be valid to prevent email enumeration
        assert serializer.is_valid()


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordResetConfirmSerializer:
    """Test PasswordResetConfirmSerializer."""

    def test_valid_data(self):
        """Test serializer with valid data."""
        serializer = PasswordResetConfirmSerializer(data={
            'token': 'test_token_123',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        })

        assert serializer.is_valid()

    def test_token_required(self):
        """Test token field is required."""
        serializer = PasswordResetConfirmSerializer(data={
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        })

        assert not serializer.is_valid()
        assert 'token' in serializer.errors

    def test_passwords_required(self):
        """Test password fields are required."""
        serializer = PasswordResetConfirmSerializer(data={
            'token': 'test_token'
        })

        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors

    def test_passwords_must_match(self):
        """Test passwords must match."""
        serializer = PasswordResetConfirmSerializer(data={
            'token': 'test_token',
            'new_password': 'Password123!',
            'new_password_confirm': 'DifferentPass123!'
        })

        assert not serializer.is_valid()
        assert 'new_password_confirm' in serializer.errors

    def test_password_validation(self):
        """Test password strength validation."""
        serializer = PasswordResetConfirmSerializer(data={
            'token': 'test_token',
            'new_password': '123',
            'new_password_confirm': '123'
        })

        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors
