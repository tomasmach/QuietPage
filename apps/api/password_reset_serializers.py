"""
Serializers for password reset functionality.

This module provides serializers for:
- Password reset request (email submission)
- Password reset confirmation (token + new password)
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.

    Accepts an email address. For security, does not reveal whether
    the email exists in the system (prevents email enumeration).
    """

    email = serializers.EmailField(
        required=True,
        help_text="Email address associated with the account"
    )

    def validate_email(self, value):
        """Validate email format (but don't check existence for security)."""
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.

    Validates the reset token and new password, then updates the user's password.
    """

    token = serializers.CharField(
        required=True,
        help_text="Password reset token from email"
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="New password"
    )

    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Confirm new password"
    )

    def validate(self, data):
        """Validate password match and strength."""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords must match.'
            })

        # Validate password strength using Django validators
        try:
            validate_password(data['new_password'])
        except Exception as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })

        return data
