"""
Settings API views for QuietPage.

This module provides REST API endpoints for user settings including:
- Profile settings (GET/PATCH)
- Goals settings (GET/PATCH)
- Privacy settings (GET/PATCH)
- Password change (POST)
- Email change (POST)
- Account deletion (POST)
- Data export download (GET)
"""

import logging
import re

from django.contrib.auth import logout, update_session_auth_hash
from django.core.files.storage import default_storage
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.middleware import log_security_event
from apps.api.settings_serializers import (
    ProfileSettingsSerializer,
    GoalsSettingsSerializer,
    PrivacySettingsSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    DeleteAccountSerializer,
)

logger = logging.getLogger(__name__)


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

        # Log security event
        log_security_event('PASSWORD_CHANGE', user, request)

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

        old_email = request.user.email
        serializer.save()

        # Log security event
        log_security_event(
            'EMAIL_CHANGE',
            request.user,
            request,
            details={'old_email': old_email, 'new_email': request.user.email}
        )

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

        # Log security event before deletion
        log_security_event('ACCOUNT_DELETION', request.user, request)

        # Delete the account
        serializer.save()

        # Logout the user (clear session)
        logout(request)

        return Response(
            {'message': 'Ucet byl uspesne smazan.'},
            status=status.HTTP_200_OK
        )


class ExportDownloadView(APIView):
    """
    API endpoint for downloading user data exports.

    GET /api/exports/download/?token=<signed_token>
    - Validates cryptographically signed token
    - Verifies token hasn't expired (48 hour limit)
    - Verifies requesting user owns the export file
    - Returns export file as downloadable attachment

    Requires authentication.

    Security:
        - Signed tokens prevent unauthorized access
        - 48-hour expiration limits exposure window
        - User ownership verification prevents cross-user access
        - Logs all download attempts for audit trail
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'export_download'

    def get(self, request):
        """Download user data export with signed token validation."""
        token = request.GET.get('token')

        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate signature and expiration (48 hours = 172800 seconds)
            signer = TimestampSigner()
            filename = signer.unsign(token, max_age=172800)

            # Validate filename format: user_{user_id}_export_{timestamp}.json
            # This prevents directory traversal and ensures user owns the file
            pattern = r'^user_(\d+)_export_\d{8}_\d{6}\.json$'
            match = re.match(pattern, filename)

            if not match:
                logger.warning(
                    f"Invalid export filename format: {filename} "
                    f"(user: {request.user.username})"
                )
                raise Http404("Export not found")

            # Extract user ID from filename and verify ownership
            file_user_id = int(match.group(1))
            if file_user_id != request.user.id:
                logger.warning(
                    f"User {request.user.username} (ID: {request.user.id}) "
                    f"attempted to access export for user ID: {file_user_id}"
                )
                log_security_event(
                    'UNAUTHORIZED_EXPORT_ACCESS',
                    request.user,
                    request,
                    details={'attempted_file': filename}
                )
                raise Http404("Export not found")

            # Construct storage path and verify file exists
            storage_path = f'exports/{filename}'
            if not default_storage.exists(storage_path):
                logger.warning(f"Export file not found: {storage_path}")
                raise Http404("Export not found")

            # Open file from storage and return as download
            file_obj = default_storage.open(storage_path, 'rb')
            response = FileResponse(
                file_obj,
                content_type='application/json',
                as_attachment=True,
                filename=f'quietpage_export_{request.user.username}.json'
            )

            logger.info(
                f"Export downloaded successfully: {filename} "
                f"(user: {request.user.username})"
            )

            return response

        except SignatureExpired:
            logger.info(f"Expired export token used by {request.user.username}")
            return Response(
                {'error': 'Download link has expired (48 hour limit)'},
                status=status.HTTP_410_GONE
            )

        except BadSignature:
            logger.warning(
                f"Invalid export token signature from {request.user.username}"
            )
            log_security_event(
                'INVALID_EXPORT_TOKEN',
                request.user,
                request,
                details={'token': token[:20] + '...'}
            )
            return Response(
                {'error': 'Invalid or tampered download link'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Http404 as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(
                f"Export download failed for {request.user.username}: {e}",
                exc_info=True
            )
            return Response(
                {'error': 'Failed to process download request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
