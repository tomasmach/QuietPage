"""
Serializers for user settings API endpoints.

This module defines serializers for:
- Profile settings (name, bio, avatar)
- Goals settings (daily word goal, timezone, reminders)
- Privacy settings (email notifications)
- Security operations (password change, email change)
- Account deletion
"""

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
import pytz

from apps.accounts.utils import resize_avatar

User = get_user_model()


class ProfileSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for profile settings (GET/PATCH).

    Handles: first_name, last_name, bio, avatar
    Avatar upload is handled with automatic resize to 512x512.
    """
    avatar = serializers.SerializerMethodField(read_only=True)
    avatar_upload = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="Avatar image file (will be resized to 512x512)"
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'bio',
            'avatar',
            'avatar_upload',
            'preferred_language',
            'preferred_theme',
        ]

    def get_avatar(self, obj):
        """Return full URL for avatar if it exists."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def validate_bio(self, value):
        """Validate bio length."""
        if value and len(value) > 500:
            raise serializers.ValidationError(
                "Bio nesmí být delší než 500 znaků."
            )
        return value

    def validate_avatar_upload(self, value):
        """
        Validate and resize avatar upload.
        Uses the existing resize_avatar utility from accounts app.
        """
        if value is None:
            return value

        try:
            # Use the existing resize_avatar utility which handles:
            # - File size validation (max 5MB)
            # - Extension whitelist
            # - Image verification
            # - Resize to 512x512
            resized = resize_avatar(value, size=(512, 512))
            return resized
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e.message))

    def update(self, instance, validated_data):
        """Update profile with avatar handling."""
        # Handle avatar upload separately
        avatar_upload = validated_data.pop('avatar_upload', None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle avatar: if avatar_upload is provided, save it
        # If avatar_upload is explicitly None (to remove avatar), clear it
        if avatar_upload is not None:
            instance.avatar = avatar_upload
        elif 'avatar_upload' in self.initial_data and self.initial_data.get('avatar_upload') is None:
            # User explicitly wants to remove avatar
            if instance.avatar:
                instance.avatar.delete(save=False)
                instance.avatar = None

        instance.save()
        return instance


class GoalsSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for goals settings (GET/PATCH).

    Handles: daily_word_goal, timezone, preferred_writing_time,
             reminder_enabled, reminder_time
    """
    timezone = serializers.CharField(
        help_text="Timezone string (e.g., 'Europe/Prague')"
    )

    class Meta:
        model = User
        fields = [
            'daily_word_goal',
            'timezone',
            'preferred_writing_time',
            'reminder_enabled',
            'reminder_time',
            'onboarding_completed',
        ]

    def validate_daily_word_goal(self, value):
        """Validate daily word goal is within allowed range."""
        if value < 100 or value > 5000:
            raise serializers.ValidationError(
                "Denni cil slov musi byt mezi 100 a 5000."
            )
        return value

    def validate_timezone(self, value):
        """Validate timezone is a valid pytz timezone."""
        try:
            pytz.timezone(str(value))
        except pytz.UnknownTimeZoneError:
            raise serializers.ValidationError(
                "Neplatna casova zona."
            )
        return value

    def validate_preferred_writing_time(self, value):
        """Validate preferred writing time is a valid choice."""
        valid_choices = ['morning', 'afternoon', 'evening', 'anytime']
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Neplatna hodnota. Povolene hodnoty: {', '.join(valid_choices)}"
            )
        return value


class PrivacySettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for privacy settings (GET/PATCH).

    Handles: email_notifications
    Note: show_stats_publicly does not exist in the model, so it's skipped.
    """

    class Meta:
        model = User
        fields = ['email_notifications']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change (POST).

    Validates current password, validates new password strength,
    and ensures new passwords match.
    """
    current_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Vase soucasne heslo"
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Nove heslo"
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Potvrzeni noveho hesla"
    )

    def validate_current_password(self, value):
        """Validate that current password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Soucasne heslo neni spravne."
            )
        return value

    def validate(self, data):
        """
        Validate new passwords match and meet strength requirements.
        """
        new_password = data.get('new_password')
        new_password_confirm = data.get('new_password_confirm')

        # Check passwords match
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Hesla se neshoduji.'
            })

        # Check new password is different from current
        user = self.context['request'].user
        if user.check_password(new_password):
            raise serializers.ValidationError({
                'new_password': 'Nove heslo musi byt jine nez soucasne.'
            })

        # Validate password strength using Django validators
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })

        return data

    def save(self):
        """Update user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ChangeEmailSerializer(serializers.Serializer):
    """
    Serializer for email change (POST).

    Initiates email change with verification flow.
    Validates password and checks email uniqueness, then creates
    EmailChangeRequest and queues verification email via Celery.
    """
    new_email = serializers.EmailField(
        required=True,
        help_text="Nova emailova adresa"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Vase soucasne heslo pro overeni"
    )

    def validate_password(self, value):
        """Validate that password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Nespravne heslo."
            )
        return value

    def validate_new_email(self, value):
        """
        Validate new email is different and not already in use.
        """
        user = self.context['request'].user

        # Check if email is the same as current
        if value.lower() == user.email.lower():
            raise serializers.ValidationError(
                "Novy email je stejny jako soucasny."
            )

        # Check if email is already in use by another user
        if User.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                "Tento email je jiz pouzivan jinym uctem."
            )

        return value

    def save(self):
        """
        Initiate email change with verification flow.

        Creates EmailChangeRequest and queues verification email via Celery.
        User email is updated only after verification link is clicked.

        Returns:
            EmailChangeRequest: The created email change request
        """
        from apps.accounts.models import EmailChangeRequest
        from apps.accounts.tasks import send_verification_email_async
        from apps.accounts.utils import generate_email_verification_token
        from django.urls import reverse
        from django.utils import timezone
        from datetime import timedelta

        user = self.context['request'].user
        new_email = self.validated_data['new_email']
        request = self.context['request']

        # Create EmailChangeRequest
        email_request = EmailChangeRequest.objects.create(
            user=user,
            new_email=new_email,
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # Generate token and URL
        token = generate_email_verification_token(user.id, new_email)
        verification_path = reverse('accounts:email-verify', kwargs={'token': token})
        verification_url = request.build_absolute_uri(verification_path)

        # Queue email task
        send_verification_email_async.delay(user.id, new_email, verification_url)

        return email_request


class DeleteAccountSerializer(serializers.Serializer):
    """
    Serializer for account deletion (POST).

    Requires password confirmation and text confirmation ("SMAZAT" or "DELETE").
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Vase heslo pro overeni"
    )
    confirmation_text = serializers.CharField(
        required=True,
        help_text="Napiste 'SMAZAT' nebo 'DELETE' pro potvrzeni smazani"
    )

    def validate_password(self, value):
        """Validate that password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Nespravne heslo."
            )
        return value

    def validate_confirmation_text(self, value):
        """Validate confirmation text is exactly 'SMAZAT' or 'DELETE'."""
        valid_confirmations = ['SMAZAT', 'DELETE']
        if value not in valid_confirmations:
            raise serializers.ValidationError(
                "Musite napsat 'SMAZAT' nebo 'DELETE' pro potvrzeni smazani uctu."
            )
        return value

    def save(self):
        """Delete user account and all associated data."""
        user = self.context['request'].user
        # Django CASCADE will delete all related data (entries, etc.)
        user.delete()
        return None
