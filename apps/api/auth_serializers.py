"""
Serializers for authentication endpoints.

This module defines serializers for login and registration operations.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login endpoint.

    Accepts either username or email along with password.
    """
    username_or_email = serializers.CharField(
        required=True,
        help_text="Username or email address"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User password"
    )


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates username and email uniqueness, password strength, and password confirmation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password (will be validated for strength)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password confirmation (must match password)"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate_username(self, value):
        """Validate username uniqueness."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Uživatel s tímto uživatelským jménem již existuje."
            )
        return value

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Uživatel s touto emailovou adresou již existuje."
            )
        return value

    def validate(self, data):
        """
        Validate password match and strength.

        Uses Django's password validators to ensure password meets security requirements.
        """
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        # Check if passwords match
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Hesla se neshodují.'
            })

        # Validate password strength using Django validators
        try:
            # Create a temporary user instance for validation
            # This allows validators to check against username, email, etc.
            user = User(
                username=data.get('username'),
                email=data.get('email')
            )
            validate_password(password, user=user)
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })

        return data

    def create(self, validated_data):
        """
        Create a new user with validated data.

        Removes password_confirm from data before creating the user.
        Uses create_user() to properly hash the password.
        """
        # Remove password_confirm as it's not a model field
        validated_data.pop('password_confirm')

        # Create user with create_user() to ensure password is hashed
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        return user
