"""
Password reset API views.

This module provides endpoints for password reset functionality:
- Request password reset (send email with token)
- Confirm password reset (validate token and change password)
"""

import logging
import secrets
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.models import PasswordResetToken
from apps.accounts.tasks import send_password_reset_email_async
from apps.api.password_reset_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetRequestView(APIView):
    """
    API endpoint for requesting password reset.

    POST /api/v1/auth/password-reset/request/
    Request: {"email": "user@example.com"}
    Response 200: {"message": "If an account exists, you will receive an email"}

    For security, always returns success to prevent email enumeration.
    Rate limited to 5 requests per hour per IP.
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset'

    def post(self, request):
        """Handle password reset request."""
        serializer = PasswordResetRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']

        try:
            # Check if user exists
            user = User.objects.get(email__iexact=email, is_active=True)

            # Generate secure token
            token = secrets.token_urlsafe(32)

            # Create password reset token
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=token
            )

            # Build reset URL
            reset_url = f"{settings.SITE_URL}/reset-password?token={token}"

            # Send email asynchronously
            send_password_reset_email_async.delay(
                user_id=user.id,
                reset_url=reset_url
            )

            logger.info(f"Password reset requested for user: {user.username}")

        except User.DoesNotExist:
            # User doesn't exist - log but return success for security
            logger.info(f"Password reset requested for nonexistent email: {email}")

        # Always return success to prevent email enumeration
        return Response(
            {'message': 'If an account exists with that email, you will receive password reset instructions.'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    API endpoint for confirming password reset.

    POST /api/v1/auth/password-reset/confirm/
    Request: {
        "token": "...",
        "new_password": "...",
        "new_password_confirm": "..."
    }
    Response 200: {"message": "Password has been reset successfully"}
    Response 400: {"error": "Invalid or expired token"}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Handle password reset confirmation."""
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        token_value = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            # Find and validate token
            reset_token = PasswordResetToken.objects.get(token=token_value)

            if not reset_token.is_valid():
                return Response(
                    {'error': 'This password reset link has expired or already been used.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update user password
            user = reset_token.user
            user.set_password(new_password)
            user.save(update_fields=['password'])

            # Mark token as used
            reset_token.mark_as_used()

            logger.info(f"Password reset completed for user: {user.username}")

            return Response(
                {'message': 'Your password has been reset successfully. You can now log in with your new password.'},
                status=status.HTTP_200_OK
            )

        except PasswordResetToken.DoesNotExist:
            logger.warning(f"Invalid password reset token attempt: {token_value[:20]}...")
            return Response(
                {'error': 'Invalid password reset link.'},
                status=status.HTTP_400_BAD_REQUEST
            )
