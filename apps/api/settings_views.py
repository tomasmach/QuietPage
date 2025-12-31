"""
Settings API views for QuietPage.

This module provides REST API endpoints for user settings including:
- Profile settings (GET/PATCH)
- Goals settings (GET/PATCH)
- Privacy settings (GET/PATCH)
- Password change (POST)
- Email change (POST)
- Account deletion (POST)
"""

from django.contrib.auth import logout, update_session_auth_hash
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.api.settings_serializers import (
    ProfileSettingsSerializer,
    GoalsSettingsSerializer,
    PrivacySettingsSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    DeleteAccountSerializer,
)


class ProfileSettingsView(APIView):
    """
    API endpoint for profile settings.

    GET /api/v1/settings/profile/
    - Returns: first_name, last_name, bio, avatar (URL)

    PATCH /api/v1/settings/profile/
    - Updates: first_name, last_name, bio, avatar_upload (file)
    - Avatar is automatically resized to 512x512

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'avatar_upload'

    def get(self, request):
        """Get current profile settings."""
        serializer = ProfileSettingsSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update profile settings."""
        serializer = ProfileSettingsSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GoalsSettingsView(APIView):
    """
    API endpoint for goals settings.

    GET /api/v1/settings/goals/
    - Returns: daily_word_goal, timezone, preferred_writing_time,
               reminder_enabled, reminder_time

    PATCH /api/v1/settings/goals/
    - Updates any of the above fields
    - daily_word_goal must be 100-5000
    - timezone must be valid pytz timezone

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current goals settings."""
        serializer = GoalsSettingsSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update goals settings."""
        serializer = GoalsSettingsSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PrivacySettingsView(APIView):
    """
    API endpoint for privacy settings.

    GET /api/v1/settings/privacy/
    - Returns: email_notifications

    PATCH /api/v1/settings/privacy/
    - Updates: email_notifications

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current privacy settings."""
        serializer = PrivacySettingsSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update privacy settings."""
        serializer = PrivacySettingsSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    API endpoint for password change.

    POST /api/v1/settings/security/password/
    - Request: {
        "current_password": "...",
        "new_password": "...",
        "new_password_confirm": "..."
      }
    - Validates current password
    - Validates new password strength using Django validators
    - Does NOT require re-login (session is updated)

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        # Update session hash so user doesn't get logged out
        update_session_auth_hash(request, user)

        return Response(
            {'message': 'Heslo bylo uspesne zmeneno.'},
            status=status.HTTP_200_OK
        )


class ChangeEmailView(APIView):
    """
    API endpoint for email change.

    POST /api/v1/settings/security/email/
    - Request: {"new_email": "...", "password": "..."}
    - Validates password
    - Checks email uniqueness
    - MVP: Updates email directly without verification

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Change user email."""
        serializer = ChangeEmailSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(
            {'message': 'Email byl uspesne zmenen.'},
            status=status.HTTP_200_OK
        )


class DeleteAccountView(APIView):
    """
    API endpoint for account deletion.

    POST /api/v1/settings/delete-account/
    - Request: {"password": "...", "confirmation_text": "SMAZAT" or "DELETE"}
    - Validates password
    - Validates confirmation text
    - Deletes user and all associated data (CASCADE)
    - Logs user out

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Delete user account."""
        serializer = DeleteAccountSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete the account
        serializer.save()

        # Logout the user (clear session)
        logout(request)

        return Response(
            {'message': 'Ucet byl uspesne smazan.'},
            status=status.HTTP_200_OK
        )
