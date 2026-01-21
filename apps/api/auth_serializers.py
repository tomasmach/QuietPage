"""
Serializers for authentication endpoints.

This module defines serializers for login and registration operations.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
import pytz
import re

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
    Includes optional onboarding fields for user preferences.
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

    # Optional onboarding fields
    preferred_theme = serializers.ChoiceField(
        choices=['midnight', 'paper'],
        required=False,
        help_text="Preferred theme (midnight or paper)"
    )
    preferred_language = serializers.ChoiceField(
        choices=['cs', 'en'],
        required=False,
        help_text="Preferred language (cs or en)"
    )
    daily_word_goal = serializers.IntegerField(
        required=False,
        validators=[MinValueValidator(100), MaxValueValidator(5000)],
        help_text="Daily word count goal (100-5000 words)"
    )
    preferred_writing_time = serializers.ChoiceField(
        choices=['morning', 'afternoon', 'evening', 'anytime'],
        required=False,
        help_text="Preferred time of day for writing"
    )
    timezone = serializers.CharField(
        required=False,
        help_text="User timezone (e.g., Europe/Prague)"
    )

    # UTM tracking fields (optional, captured from URL params)
    utm_source = serializers.CharField(
        required=False,
        max_length=100,
        allow_blank=True,
        help_text="Traffic source (e.g., reddit, twitter, hackernews)"
    )
    utm_medium = serializers.CharField(
        required=False,
        max_length=100,
        allow_blank=True,
        help_text="Marketing medium (e.g., social, referral, email)"
    )
    utm_campaign = serializers.CharField(
        required=False,
        max_length=100,
        allow_blank=True,
        help_text="Campaign name (e.g., launch-week-1)"
    )
    referrer = serializers.URLField(
        required=False,
        max_length=500,
        allow_blank=True,
        help_text="Full referrer URL when user first visited"
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'preferred_theme', 'preferred_language', 'daily_word_goal',
            'preferred_writing_time', 'timezone',
            'utm_source', 'utm_medium', 'utm_campaign', 'referrer'
        ]

    def validate_username(self, value):
        """Validate username format and uniqueness."""
        # Pouze alfanumerické znaky, podtržítko a tečka
        if not re.match(r'^[a-zA-Z0-9_.]+$', value):
            raise serializers.ValidationError(
                "Uživatelské jméno může obsahovat pouze písmena, čísla, podtržítko a tečku."
            )

        # Minimální délka
        if len(value) < 3:
            raise serializers.ValidationError(
                "Uživatelské jméno musí mít alespoň 3 znaky."
            )

        # Maximální délka
        if len(value) > 30:
            raise serializers.ValidationError(
                "Uživatelské jméno může mít maximálně 30 znaků."
            )

        # Existující unique check
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Toto uživatelské jméno je již obsazené."
            )
        return value

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Uživatel s touto emailovou adresou již existuje."
            )
        return value

    def validate_timezone(self, value):
        """Validate timezone string."""
        if value:
            try:
                pytz.timezone(value)
            except pytz.exceptions.UnknownTimeZoneError:
                raise serializers.ValidationError(
                    f"Neplatná časová zóna: {value}"
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
        Saves optional onboarding fields if provided.
        """
        # Remove password_confirm as it's not a model field
        validated_data.pop('password_confirm')

        # Extract required fields
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # Create user with create_user() to ensure password is hashed
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Update optional onboarding fields if provided
        # All fields have defaults in the model, so this is safe
        optional_fields = [
            'preferred_theme', 'preferred_language', 'daily_word_goal',
            'preferred_writing_time', 'timezone',
            'utm_source', 'utm_medium', 'utm_campaign', 'referrer'
        ]
        for field in optional_fields:
            if field in validated_data:
                setattr(user, field, validated_data[field])

        # Save user with optional fields
        if any(field in validated_data for field in optional_fields):
            user.save()

        return user
