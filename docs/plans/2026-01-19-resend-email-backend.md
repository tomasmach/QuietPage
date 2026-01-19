# Resend Email Backend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate Resend email service with Django backend for transactional emails (registration, password reset, email verification, account deletion).

**Architecture:** Custom Django email backend using Resend Python SDK, async email sending via Celery, cryptographically signed tokens for password reset and email verification.

**Tech Stack:** Resend Python SDK, Django email backend, Celery, TimestampSigner for tokens, plain text email templates.

---

## Task 1: Install Resend SDK and Configure Settings

**Files:**
- Modify: `requirements/base.txt`
- Modify: `config/settings/base.py`
- Modify: `.env.example`

**Step 1: Add Resend dependency**

Add to `requirements/base.txt` after line 42:
```
# Email service
resend==2.5.1
```

**Step 2: Update environment example**

Add to `.env.example`:
```
# Email Configuration
RESEND_API_KEY=your_resend_api_key_here
DEFAULT_FROM_EMAIL=info@quietpage.app
```

**Step 3: Update base settings**

Add to `config/settings/base.py` after line 344 (after SITE_URL):
```python
# ============================================
# EMAIL CONFIGURATION
# ============================================
# Email backend (Resend for production, console for development)
EMAIL_BACKEND = 'apps.core.backends.resend_backend.ResendEmailBackend'

# Resend API configuration
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
if not RESEND_API_KEY:
    raise ImproperlyConfigured(
        'RESEND_API_KEY environment variable is required.\n'
        'Get your API key from: https://resend.com/api-keys'
    )

# Email sender configuration
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'info@quietpage.app')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
```

**Step 4: Commit**

```bash
git add requirements/base.txt config/settings/base.py .env.example
git commit -m "chore: add Resend SDK and email configuration"
```

---

## Task 2: Create Resend Email Backend

**Files:**
- Create: `apps/core/backends/__init__.py`
- Create: `apps/core/backends/resend_backend.py`

**Step 1: Create backends package**

Create `apps/core/backends/__init__.py`:
```python
"""Custom email backends for QuietPage."""
```

**Step 2: Write Resend backend test**

Create `apps/core/tests/test_resend_backend.py`:
```python
"""Tests for Resend email backend."""

import pytest
from unittest.mock import patch, MagicMock
from django.core.mail import send_mail
from django.test import override_settings


@pytest.mark.unit
@override_settings(
    EMAIL_BACKEND='apps.core.backends.resend_backend.ResendEmailBackend',
    RESEND_API_KEY='test_api_key'
)
class TestResendBackend:
    """Test Resend email backend integration."""

    @patch('apps.core.backends.resend_backend.resend.Emails.send')
    def test_send_single_email(self, mock_send):
        """Test sending a single email via Resend."""
        mock_send.return_value = {'id': 'test_email_id'}

        result = send_mail(
            subject='Test Subject',
            message='Test message body',
            from_email='info@quietpage.app',
            recipient_list=['user@example.com'],
            fail_silently=False
        )

        assert result == 1
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args['from'] == 'info@quietpage.app'
        assert call_args['to'] == ['user@example.com']
        assert call_args['subject'] == 'Test Subject'
        assert call_args['text'] == 'Test message body'

    @patch('apps.core.backends.resend_backend.resend.Emails.send')
    def test_send_email_failure(self, mock_send):
        """Test email sending failure handling."""
        mock_send.side_effect = Exception('API Error')

        with pytest.raises(Exception, match='API Error'):
            send_mail(
                subject='Test',
                message='Test',
                from_email='info@quietpage.app',
                recipient_list=['user@example.com'],
                fail_silently=False
            )

    @patch('apps.core.backends.resend_backend.resend.Emails.send')
    def test_send_email_multiple_recipients(self, mock_send):
        """Test sending email to multiple recipients."""
        mock_send.return_value = {'id': 'test_email_id'}

        result = send_mail(
            subject='Test',
            message='Test',
            from_email='info@quietpage.app',
            recipient_list=['user1@example.com', 'user2@example.com'],
            fail_silently=False
        )

        assert result == 1
        call_args = mock_send.call_args[0][0]
        assert call_args['to'] == ['user1@example.com', 'user2@example.com']
```

**Step 3: Run test to verify it fails**

```bash
uv run pytest apps/core/tests/test_resend_backend.py -v
```
Expected: FAIL - module not found

**Step 4: Implement Resend backend**

Create `apps/core/backends/resend_backend.py`:
```python
"""
Custom Django email backend using Resend.

This backend integrates Resend's email API with Django's email system.
"""

import logging
import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """
    Email backend that sends emails using Resend API.

    Configuration:
        - RESEND_API_KEY: Your Resend API key (required)
        - DEFAULT_FROM_EMAIL: Default sender email address
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        resend.api_key = settings.RESEND_API_KEY

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number sent.

        Args:
            email_messages: List of Django EmailMessage objects

        Returns:
            int: Number of emails sent successfully
        """
        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send_message(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email via Resend: {e}", exc_info=True)
                if not self.fail_silently:
                    raise

        return num_sent

    def _send_message(self, message):
        """
        Send a single EmailMessage via Resend API.

        Args:
            message: Django EmailMessage object

        Returns:
            bool: True if email was sent successfully
        """
        if not message.recipients():
            return False

        # Prepare email parameters for Resend
        params = {
            'from': message.from_email or settings.DEFAULT_FROM_EMAIL,
            'to': message.recipients(),
            'subject': message.subject,
        }

        # Add plain text body
        if message.body:
            params['text'] = message.body

        # Send via Resend API
        response = resend.Emails.send(params)

        logger.info(
            f"Email sent via Resend: {message.subject} "
            f"to {len(message.recipients())} recipient(s) "
            f"(id: {response.get('id', 'unknown')})"
        )

        return True
```

**Step 5: Run tests to verify they pass**

```bash
uv run pytest apps/core/tests/test_resend_backend.py -v
```
Expected: PASS (3 tests)

**Step 6: Commit**

```bash
git add apps/core/backends/ apps/core/tests/test_resend_backend.py
git commit -m "feat: add Resend email backend"
```

---

## Task 3: Create PasswordResetToken Model

**Files:**
- Modify: `apps/accounts/models.py`
- Create migration

**Step 1: Write model test**

Add to `apps/accounts/tests/test_models.py`:
```python
from datetime import timedelta
from django.utils import timezone
import pytest


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordResetToken:
    """Test PasswordResetToken model."""

    def test_create_reset_token(self, user_factory):
        """Test creating a password reset token."""
        from apps.accounts.models import PasswordResetToken

        user = user_factory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='test_token_123'
        )

        assert token.user == user
        assert token.token == 'test_token_123'
        assert token.is_used is False
        assert token.used_at is None
        assert token.expires_at > timezone.now()

    def test_token_expires_in_one_hour(self, user_factory):
        """Test token expiration is set to 1 hour."""
        from apps.accounts.models import PasswordResetToken

        user = user_factory()
        before = timezone.now() + timedelta(hours=1)

        token = PasswordResetToken.objects.create(
            user=user,
            token='test_token'
        )

        after = timezone.now() + timedelta(hours=1)

        assert before <= token.expires_at <= after

    def test_is_valid_with_valid_token(self, user_factory):
        """Test is_valid returns True for valid token."""
        from apps.accounts.models import PasswordResetToken

        user = user_factory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='test_token'
        )

        assert token.is_valid() is True

    def test_is_valid_with_expired_token(self, user_factory):
        """Test is_valid returns False for expired token."""
        from apps.accounts.models import PasswordResetToken

        user = user_factory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='test_token',
            expires_at=timezone.now() - timedelta(hours=1)
        )

        assert token.is_valid() is False

    def test_is_valid_with_used_token(self, user_factory):
        """Test is_valid returns False for used token."""
        from apps.accounts.models import PasswordResetToken

        user = user_factory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='test_token',
            is_used=True,
            used_at=timezone.now()
        )

        assert token.is_valid() is False

    def test_mark_as_used(self, user_factory):
        """Test marking token as used."""
        from apps.accounts.models import PasswordResetToken

        user = user_factory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='test_token'
        )

        token.mark_as_used()

        assert token.is_used is True
        assert token.used_at is not None
        assert token.is_valid() is False
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest apps/accounts/tests/test_models.py::TestPasswordResetToken -v
```
Expected: FAIL - PasswordResetToken does not exist

**Step 3: Add PasswordResetToken model**

Add to `apps/accounts/models.py` after EmailChangeRequest class (after line 208):
```python


class PasswordResetToken(models.Model):
    """
    Model for password reset tokens.

    When a user requests a password reset, a token is generated and stored here.
    The token is sent via email and can be used once within the expiration window.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        help_text="User requesting the password reset"
    )

    token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique token for password reset"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the reset was requested"
    )

    expires_at = models.DateTimeField(
        help_text="When this token expires (default: 1 hour)"
    )

    is_used = models.BooleanField(
        default=False,
        help_text="Whether the token has been used"
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the token was used"
    )

    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'is_used', 'expires_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        """Set expiry time on creation if not provided."""
        if not self.pk and not self.expires_at:
            # Default expiration: 1 hour from now
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if this token is valid (not expired and not used)."""
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True

    def mark_as_used(self):
        """Mark this token as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])

    def __str__(self):
        status = "used" if self.is_used else "active"
        return f"{self.user.username} - {status} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
```

**Step 4: Create migration**

```bash
uv run python manage.py makemigrations accounts -n add_password_reset_token
```
Expected: Migration created successfully

**Step 5: Run migration**

```bash
uv run python manage.py migrate
```
Expected: Migration applied

**Step 6: Run tests to verify they pass**

```bash
uv run pytest apps/accounts/tests/test_models.py::TestPasswordResetToken -v
```
Expected: PASS (6 tests)

**Step 7: Commit**

```bash
git add apps/accounts/models.py apps/accounts/tests/test_models.py apps/accounts/migrations/
git commit -m "feat: add PasswordResetToken model"
```

---

## Task 4: Create Email Templates

**Files:**
- Create: `templates/accounts/emails/welcome.txt`
- Create: `templates/accounts/emails/password_reset_request.txt`
- Create: `templates/accounts/emails/password_changed.txt`
- Modify: `templates/accounts/emails/email_verification.txt`
- Create: `templates/accounts/emails/email_changed_notification.txt`
- Create: `templates/accounts/emails/account_deleted.txt`

**Step 1: Create welcome email template**

Create `templates/accounts/emails/welcome.txt`:
```
QuietPage - Welcome!
====================

Hello {{ user.first_name|default:user.username }},

Welcome to QuietPage - your safe space for writing and reflection.

Your account has been successfully created. You can now:
- Write daily journal entries
- Track your writing streak
- Analyze your mood patterns
- Export your data anytime

Start writing: {{ dashboard_url }}

Tips for getting started:
- Set your daily word goal in Settings
- Enable writing reminders to build a habit
- Use tags to organize your thoughts

---
QuietPage - Your safe space for writing
This email was sent from an automated system.
```

**Step 2: Create password reset request template**

Create `templates/accounts/emails/password_reset_request.txt`:
```
QuietPage - Password Reset
===========================

Hello {{ user.first_name|default:user.username }},

We received a request to reset your password.

To reset your password, click this link:
{{ reset_url }}

IMPORTANT:
- This link will expire in 1 hour
- If you didn't request this reset, please ignore this email
- Your password will remain unchanged unless you click the link

For security, never share this link with anyone.

---
QuietPage - Your safe space for writing
This email was sent from an automated system.
```

**Step 3: Create password changed notification template**

Create `templates/accounts/emails/password_changed.txt`:
```
QuietPage - Password Changed
=============================

Hello {{ user.first_name|default:user.username }},

Your password was successfully changed.

Time: {{ timestamp }}
IP Address: {{ ip_address }}

If you made this change, no action is needed.

If you did NOT change your password, please:
1. Reset your password immediately: {{ reset_url }}
2. Contact support if you need help

---
QuietPage - Your safe space for writing
This email was sent from an automated system.
```

**Step 4: Update email verification template**

Replace content of `templates/accounts/emails/email_verification.txt`:
```
QuietPage - Verify Email Address
=================================

Hello {{ user.first_name|default:user.username }},

We received a request to change your account email address to:
{{ new_email }}

To complete the change, click this link:
{{ verification_url }}

IMPORTANT:
- This link will expire in 24 hours
- If you didn't request this change, please ignore this email
- Your email will remain unchanged unless you click the link

---
QuietPage - Your safe space for writing
This email was sent from an automated system.
```

**Step 5: Create email changed notification template**

Create `templates/accounts/emails/email_changed_notification.txt`:
```
QuietPage - Email Address Changed
==================================

Hello {{ user.first_name|default:user.username }},

Your account email address was successfully changed.

Old email: {{ old_email }}
New email: {{ new_email }}
Time: {{ timestamp }}

If you made this change, no action is needed.

If you did NOT change your email address, please contact support immediately.

---
QuietPage - Your safe space for writing
This email was sent to your old email address as a security notification.
```

**Step 6: Create account deleted template**

Create `templates/accounts/emails/account_deleted.txt`:
```
QuietPage - Account Deleted
============================

Hello {{ username }},

Your QuietPage account has been successfully deleted.

All your data, including journal entries, has been permanently removed from our servers.

We're sorry to see you go. If you change your mind, you can always create a new account.

Thank you for using QuietPage.

---
QuietPage - Your safe space for writing
This email was sent from an automated system.
```

**Step 7: Commit**

```bash
git add templates/accounts/emails/
git commit -m "feat: add email templates for all transactional emails"
```

---

## Task 5: Create Password Reset Serializers

**Files:**
- Create: `apps/api/password_reset_serializers.py`

**Step 1: Write serializer tests**

Create `apps/api/tests/test_password_reset_serializers.py`:
```python
"""Tests for password reset serializers."""

import pytest
from django.contrib.auth import get_user_model
from apps.api.password_reset_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordResetRequestSerializer:
    """Test PasswordResetRequestSerializer."""

    def test_valid_email(self, user_factory):
        """Test serializer with valid email."""
        user = user_factory(email='test@example.com')

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
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest apps/api/tests/test_password_reset_serializers.py -v
```
Expected: FAIL - module not found

**Step 3: Implement serializers**

Create `apps/api/password_reset_serializers.py`:
```python
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
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest apps/api/tests/test_password_reset_serializers.py -v
```
Expected: PASS (11 tests)

**Step 5: Commit**

```bash
git add apps/api/password_reset_serializers.py apps/api/tests/test_password_reset_serializers.py
git commit -m "feat: add password reset serializers"
```

---

## Task 6: Create Password Reset Views

**Files:**
- Create: `apps/api/password_reset_views.py`
- Modify: `apps/api/urls.py`

**Step 1: Write view tests**

Create `apps/api/tests/test_password_reset_views.py`:
```python
"""Tests for password reset views."""

import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from apps.accounts.models import PasswordResetToken

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordResetRequestView:
    """Test password reset request endpoint."""

    def test_request_reset_with_valid_email(self, api_client, user_factory):
        """Test requesting password reset with valid email."""
        user = user_factory(email='test@example.com')
        url = reverse('api:auth:password-reset-request')

        with patch('apps.api.password_reset_views.send_password_reset_email_async.delay') as mock_task:
            response = api_client.post(url, {
                'email': 'test@example.com'
            })

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

        # Verify token was created
        assert PasswordResetToken.objects.filter(user=user).exists()

        # Verify email task was called
        mock_task.assert_called_once()

    def test_request_reset_with_nonexistent_email(self, api_client):
        """Test requesting reset with nonexistent email (should succeed for security)."""
        url = reverse('api:auth:password-reset-request')

        response = api_client.post(url, {
            'email': 'nonexistent@example.com'
        })

        # Should return success to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

    def test_request_reset_with_invalid_email(self, api_client):
        """Test requesting reset with invalid email format."""
        url = reverse('api:auth:password-reset-request')

        response = api_client.post(url, {
            'email': 'not-an-email'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_request_reset_rate_limiting(self, api_client, user_factory):
        """Test rate limiting on password reset requests."""
        user = user_factory(email='test@example.com')
        url = reverse('api:auth:password-reset-request')

        # Make multiple requests
        for i in range(6):
            response = api_client.post(url, {
                'email': 'test@example.com'
            })

            if i < 5:
                assert response.status_code == status.HTTP_200_OK
            else:
                # 6th request should be throttled
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordResetConfirmView:
    """Test password reset confirmation endpoint."""

    def test_confirm_reset_with_valid_token(self, api_client, user_factory):
        """Test confirming password reset with valid token."""
        user = user_factory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='valid_test_token'
        )

        url = reverse('api:auth:password-reset-confirm')
        response = api_client.post(url, {
            'token': 'valid_test_token',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        })

        assert response.status_code == status.HTTP_200_OK

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password('NewSecurePass123!')

        # Verify token was marked as used
        token.refresh_from_db()
        assert token.is_used is True

    def test_confirm_reset_with_invalid_token(self, api_client):
        """Test confirming reset with invalid token."""
        url = reverse('api:auth:password-reset-confirm')
        response = api_client.post(url, {
            'token': 'invalid_token',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_confirm_reset_with_expired_token(self, api_client, user_factory):
        """Test confirming reset with expired token."""
        from django.utils import timezone
        from datetime import timedelta

        user = user_factory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='expired_token',
            expires_at=timezone.now() - timedelta(hours=1)
        )

        url = reverse('api:auth:password-reset-confirm')
        response = api_client.post(url, {
            'token': 'expired_token',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_with_used_token(self, api_client, user_factory):
        """Test confirming reset with already used token."""
        user = user_factory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='used_token',
            is_used=True
        )

        url = reverse('api:auth:password-reset-confirm')
        response = api_client.post(url, {
            'token': 'used_token',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_with_weak_password(self, api_client, user_factory):
        """Test confirming reset with weak password."""
        user = user_factory()
        token = PasswordResetToken.objects.create(
            user=user,
            token='valid_token'
        )

        url = reverse('api:auth:password-reset-confirm')
        response = api_client.post(url, {
            'token': 'valid_token',
            'new_password': '123',
            'new_password_confirm': '123'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest apps/api/tests/test_password_reset_views.py -v
```
Expected: FAIL - module not found

**Step 3: Implement password reset views**

Create `apps/api/password_reset_views.py`:
```python
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
```

**Step 4: Add URL routes**

Add to `apps/api/urls.py` in the auth_patterns list:
```python
# Password reset
path('password-reset/request/', password_reset_views.PasswordResetRequestView.as_view(), name='password-reset-request'),
path('password-reset/confirm/', password_reset_views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
```

And add import at top:
```python
from apps.api import password_reset_views
```

**Step 5: Add throttle scope to settings**

Add to `config/settings/base.py` in REST_FRAMEWORK DEFAULT_THROTTLE_RATES dict:
```python
'password_reset': '5/hour',
```

**Step 6: Run tests to verify they pass**

```bash
uv run pytest apps/api/tests/test_password_reset_views.py -v
```
Expected: PASS (10 tests)

**Step 7: Commit**

```bash
git add apps/api/password_reset_views.py apps/api/tests/test_password_reset_views.py apps/api/urls.py config/settings/base.py
git commit -m "feat: add password reset API endpoints"
```

---

## Task 7: Update Email Change Flow with Verification

**Files:**
- Modify: `apps/api/settings_views.py`
- Modify: `apps/api/urls.py`

**Step 1: Write email verification endpoint test**

Add to `apps/api/tests/test_settings_views.py`:
```python
@pytest.mark.integration
@pytest.mark.django_db
class TestEmailChangeVerifyView:
    """Test email change verification endpoint."""

    def test_verify_valid_token(self, api_client, user_factory):
        """Test verifying email change with valid token."""
        from apps.accounts.models import EmailChangeRequest
        from django.utils import timezone
        from datetime import timedelta

        user = user_factory(email='old@example.com')
        api_client.force_authenticate(user=user)

        # Create email change request
        request = EmailChangeRequest.objects.create(
            user=user,
            new_email='new@example.com',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        url = reverse('api:auth:email-change-verify', kwargs={'token': str(request.pk)})

        with patch('apps.api.settings_views.send_email_changed_notification_async.delay'):
            response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Verify email was updated
        user.refresh_from_db()
        assert user.email == 'new@example.com'

        # Verify request was marked as verified
        request.refresh_from_db()
        assert request.is_verified is True

    def test_verify_expired_token(self, api_client, user_factory):
        """Test verifying email change with expired token."""
        from apps.accounts.models import EmailChangeRequest
        from django.utils import timezone
        from datetime import timedelta

        user = user_factory(email='old@example.com')
        api_client.force_authenticate(user=user)

        # Create expired request
        request = EmailChangeRequest.objects.create(
            user=user,
            new_email='new@example.com',
            expires_at=timezone.now() - timedelta(hours=1)
        )

        url = reverse('api:auth:email-change-verify', kwargs={'token': str(request.pk)})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_already_verified_token(self, api_client, user_factory):
        """Test verifying already verified email change."""
        from apps.accounts.models import EmailChangeRequest
        from django.utils import timezone
        from datetime import timedelta

        user = user_factory(email='old@example.com')
        api_client.force_authenticate(user=user)

        # Create already verified request
        request = EmailChangeRequest.objects.create(
            user=user,
            new_email='new@example.com',
            expires_at=timezone.now() + timedelta(hours=24),
            is_verified=True,
            verified_at=timezone.now()
        )

        url = reverse('api:auth:email-change-verify', kwargs={'token': str(request.pk)})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest apps/api/tests/test_settings_views.py::TestEmailChangeVerifyView -v
```
Expected: FAIL - view does not exist

**Step 3: Update ChangeEmailView to use verification**

Replace the `ChangeEmailView` class in `apps/api/settings_views.py`:
```python
class ChangeEmailView(APIView):
    """
    API endpoint for email change.

    POST /api/v1/settings/security/email/
    - Request: {"new_email": "...", "password": "..."}
    - Validates password
    - Checks email uniqueness
    - Creates EmailChangeRequest and sends verification email
    - Email is updated only after verification

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'email_change'

    def post(self, request):
        """Request email change with verification."""
        serializer = ChangeEmailSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_email = serializer.validated_data['new_email']

        # Create email change request
        from apps.accounts.models import EmailChangeRequest
        from datetime import timedelta
        from django.utils import timezone

        email_request = EmailChangeRequest.objects.create(
            user=request.user,
            new_email=new_email,
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # Build verification URL
        from django.conf import settings
        verification_url = f"{settings.SITE_URL}/verify-email?token={email_request.pk}"

        # Send verification email asynchronously
        from apps.accounts.tasks import send_email_change_verification_async
        send_email_change_verification_async.delay(
            user_id=request.user.id,
            new_email=new_email,
            verification_url=verification_url
        )

        return Response(
            {'message': f'Verification email sent to {new_email}. Please check your inbox.'},
            status=status.HTTP_200_OK
        )
```

**Step 4: Add email change verification view**

Add after ChangeEmailView in `apps/api/settings_views.py`:
```python


class EmailChangeVerifyView(APIView):
    """
    API endpoint for email change verification.

    GET /api/v1/auth/email-change/verify/<token>/
    - Validates token (EmailChangeRequest ID)
    - Checks token hasn't expired
    - Updates user email
    - Sends notification to old email

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, token):
        """Verify email change token and update user email."""
        try:
            from apps.accounts.models import EmailChangeRequest
            from django.utils import timezone

            # Find email change request
            email_request = EmailChangeRequest.objects.get(
                pk=token,
                user=request.user
            )

            # Check if already verified
            if email_request.is_verified:
                return Response(
                    {'error': 'This email has already been verified.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if expired
            if email_request.is_expired():
                return Response(
                    {'error': 'This verification link has expired.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Store old email for notification
            old_email = request.user.email

            # Update user email
            request.user.email = email_request.new_email
            request.user.save(update_fields=['email'])

            # Mark request as verified
            email_request.is_verified = True
            email_request.verified_at = timezone.now()
            email_request.save(update_fields=['is_verified', 'verified_at'])

            # Log security event
            log_security_event(
                'EMAIL_CHANGE',
                request.user,
                request,
                details={'old_email': old_email, 'new_email': email_request.new_email}
            )

            # Send notification to old email
            from apps.accounts.tasks import send_email_changed_notification_async
            send_email_changed_notification_async.delay(
                user_id=request.user.id,
                old_email=old_email,
                new_email=email_request.new_email
            )

            return Response(
                {'message': 'Email address updated successfully.'},
                status=status.HTTP_200_OK
            )

        except EmailChangeRequest.DoesNotExist:
            return Response(
                {'error': 'Invalid verification link.'},
                status=status.HTTP_400_BAD_REQUEST
            )
```

**Step 5: Add URL route**

Add to `apps/api/urls.py` in auth_patterns:
```python
# Email verification
path('email-change/verify/<int:token>/', settings_views.EmailChangeVerifyView.as_view(), name='email-change-verify'),
```

**Step 6: Add throttle scope**

Add to `config/settings/base.py` in REST_FRAMEWORK DEFAULT_THROTTLE_RATES dict:
```python
'email_change': '3/hour',
```

**Step 7: Run tests to verify they pass**

```bash
uv run pytest apps/api/tests/test_settings_views.py::TestEmailChangeVerifyView -v
```
Expected: PASS (3 tests)

**Step 8: Commit**

```bash
git add apps/api/settings_views.py apps/api/urls.py apps/api/tests/test_settings_views.py config/settings/base.py
git commit -m "feat: add email verification for email changes"
```

---

## Task 8: Create Celery Email Tasks

**Files:**
- Modify: `apps/accounts/tasks.py`

**Step 1: Write email task tests**

Create `apps/accounts/tests/test_email_tasks.py`:
```python
"""Tests for email sending tasks."""

import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestWelcomeEmail:
    """Test welcome email task."""

    @patch('apps.accounts.tasks.send_mail')
    def test_send_welcome_email(self, mock_send_mail, user_factory):
        """Test sending welcome email."""
        from apps.accounts.tasks import send_welcome_email_async

        user = user_factory(email='test@example.com')

        result = send_welcome_email_async(user_id=user.id)

        assert result is True
        mock_send_mail.assert_called_once()

        # Verify email content
        call_args = mock_send_mail.call_args
        assert 'Welcome' in call_args[1]['subject']
        assert user.email in call_args[1]['recipient_list']


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordResetEmail:
    """Test password reset email task."""

    @patch('apps.accounts.tasks.send_mail')
    def test_send_password_reset_email(self, mock_send_mail, user_factory):
        """Test sending password reset email."""
        from apps.accounts.tasks import send_password_reset_email_async

        user = user_factory(email='test@example.com')
        reset_url = 'https://example.com/reset?token=abc123'

        result = send_password_reset_email_async(
            user_id=user.id,
            reset_url=reset_url
        )

        assert result is True
        mock_send_mail.assert_called_once()

        # Verify email content includes reset URL
        call_args = mock_send_mail.call_args
        assert 'Password Reset' in call_args[1]['subject']
        assert reset_url in call_args[1]['message']


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordChangedEmail:
    """Test password changed notification email task."""

    @patch('apps.accounts.tasks.send_mail')
    def test_send_password_changed_email(self, mock_send_mail, user_factory):
        """Test sending password changed notification."""
        from apps.accounts.tasks import send_password_changed_email_async

        user = user_factory(email='test@example.com')
        ip_address = '192.168.1.1'

        result = send_password_changed_email_async(
            user_id=user.id,
            ip_address=ip_address
        )

        assert result is True
        mock_send_mail.assert_called_once()

        # Verify email content
        call_args = mock_send_mail.call_args
        assert 'Password Changed' in call_args[1]['subject']
        assert ip_address in call_args[1]['message']


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailChangedNotification:
    """Test email changed notification task."""

    @patch('apps.accounts.tasks.send_mail')
    def test_send_email_changed_notification(self, mock_send_mail, user_factory):
        """Test sending email changed notification to old address."""
        from apps.accounts.tasks import send_email_changed_notification_async

        user = user_factory()
        old_email = 'old@example.com'
        new_email = 'new@example.com'

        result = send_email_changed_notification_async(
            user_id=user.id,
            old_email=old_email,
            new_email=new_email
        )

        assert result is True
        mock_send_mail.assert_called_once()

        # Verify sent to old email
        call_args = mock_send_mail.call_args
        assert old_email in call_args[1]['recipient_list']
        assert 'Email Address Changed' in call_args[1]['subject']


@pytest.mark.unit
@pytest.mark.django_db
class TestAccountDeletedEmail:
    """Test account deleted email task."""

    @patch('apps.accounts.tasks.send_mail')
    def test_send_account_deleted_email(self, mock_send_mail):
        """Test sending account deletion confirmation."""
        from apps.accounts.tasks import send_account_deleted_email_async

        email = 'deleted@example.com'
        username = 'testuser'

        result = send_account_deleted_email_async(
            email=email,
            username=username
        )

        assert result is True
        mock_send_mail.assert_called_once()

        # Verify email content
        call_args = mock_send_mail.call_args
        assert 'Account Deleted' in call_args[1]['subject']
        assert email in call_args[1]['recipient_list']
        assert username in call_args[1]['message']
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest apps/accounts/tests/test_email_tasks.py -v
```
Expected: FAIL - functions don't exist

**Step 3: Add new email tasks**

Add to `apps/accounts/tasks.py` after the existing `send_reminder_emails` task:
```python


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_async(self, user_id):
    """
    Send welcome email after registration.

    Args:
        user_id (int): User ID who just registered

    Returns:
        bool: True if email sent successfully
    """
    try:
        user = User.objects.get(pk=user_id)

        context = {
            'user': user,
            'dashboard_url': settings.SITE_URL,
        }

        plain_message = render_to_string('accounts/emails/welcome.txt', context)

        send_mail(
            subject='Welcome to QuietPage!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

        logger.info(f"Welcome email sent to user_id={user_id}")
        return True

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found, cannot send welcome email")
        return False

    except Exception as e:
        logger.error(f"Failed to send welcome email for user_id={user_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_async(self, user_id, reset_url):
    """
    Send password reset email with reset link.

    Args:
        user_id (int): User ID requesting password reset
        reset_url (str): Full password reset URL with token

    Returns:
        bool: True if email sent successfully
    """
    try:
        user = User.objects.get(pk=user_id)

        context = {
            'user': user,
            'reset_url': reset_url,
        }

        plain_message = render_to_string('accounts/emails/password_reset_request.txt', context)

        send_mail(
            subject='QuietPage - Password Reset',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

        logger.info(f"Password reset email sent to user_id={user_id}")
        return True

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found, cannot send password reset email")
        return False

    except Exception as e:
        logger.error(f"Failed to send password reset email for user_id={user_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_changed_email_async(self, user_id, ip_address='unknown'):
    """
    Send notification email after password change.

    Args:
        user_id (int): User ID whose password was changed
        ip_address (str): IP address where change was made

    Returns:
        bool: True if email sent successfully
    """
    try:
        user = User.objects.get(pk=user_id)

        context = {
            'user': user,
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'ip_address': ip_address,
            'reset_url': f"{settings.SITE_URL}/reset-password",
        }

        plain_message = render_to_string('accounts/emails/password_changed.txt', context)

        send_mail(
            subject='QuietPage - Password Changed',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

        logger.info(f"Password changed notification sent to user_id={user_id}")
        return True

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found, cannot send password changed email")
        return False

    except Exception as e:
        logger.error(f"Failed to send password changed email for user_id={user_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_change_verification_async(self, user_id, new_email, verification_url):
    """
    Send email verification link to new email address.

    Args:
        user_id (int): User ID requesting email change
        new_email (str): New email address to verify
        verification_url (str): Full verification URL with token

    Returns:
        bool: True if email sent successfully
    """
    try:
        user = User.objects.get(pk=user_id)

        context = {
            'user': user,
            'new_email': new_email,
            'verification_url': verification_url,
        }

        plain_message = render_to_string('accounts/emails/email_verification.txt', context)

        send_mail(
            subject='QuietPage - Verify Email Address',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_email],
            fail_silently=False
        )

        logger.info(f"Email verification sent to {new_email} for user_id={user_id}")
        return True

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found, cannot send email verification")
        return False

    except Exception as e:
        logger.error(f"Failed to send email verification for user_id={user_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_changed_notification_async(self, user_id, old_email, new_email):
    """
    Send notification to old email address after email change.

    Args:
        user_id (int): User ID whose email was changed
        old_email (str): Previous email address
        new_email (str): New email address

    Returns:
        bool: True if email sent successfully
    """
    try:
        user = User.objects.get(pk=user_id)

        context = {
            'user': user,
            'old_email': old_email,
            'new_email': new_email,
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        }

        plain_message = render_to_string('accounts/emails/email_changed_notification.txt', context)

        # Send to OLD email as security notification
        send_mail(
            subject='QuietPage - Email Address Changed',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[old_email],
            fail_silently=False
        )

        logger.info(f"Email change notification sent to {old_email} for user_id={user_id}")
        return True

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found, cannot send email change notification")
        return False

    except Exception as e:
        logger.error(f"Failed to send email change notification for user_id={user_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_account_deleted_email_async(self, email, username):
    """
    Send confirmation email after account deletion.

    Args:
        email (str): User's email address
        username (str): Username of deleted account

    Returns:
        bool: True if email sent successfully
    """
    try:
        context = {
            'username': username,
        }

        plain_message = render_to_string('accounts/emails/account_deleted.txt', context)

        send_mail(
            subject='QuietPage - Account Deleted',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )

        logger.info(f"Account deletion confirmation sent to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send account deletion email to {email}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest apps/accounts/tests/test_email_tasks.py -v
```
Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add apps/accounts/tasks.py apps/accounts/tests/test_email_tasks.py
git commit -m "feat: add Celery tasks for all transactional emails"
```

---

## Task 9: Wire Up Registration to Send Welcome Email

**Files:**
- Modify: `apps/api/auth_views.py`

**Step 1: Update registration view to send welcome email**

In `apps/api/auth_views.py`, update the `RegisterView.post` method. After line 153 (`login(request, user, backend='django.contrib.auth.backends.ModelBackend')`), add:

```python
        # Send welcome email asynchronously
        from apps.accounts.tasks import send_welcome_email_async
        send_welcome_email_async.delay(user_id=user.id)
```

**Step 2: Update registration test**

In `apps/api/tests/test_auth_views.py`, add mock for welcome email in registration test:

```python
@patch('apps.api.auth_views.send_welcome_email_async.delay')
def test_register_success(self, mock_welcome_email, api_client):
    """Test successful registration sends welcome email."""
    # ... existing test code ...

    # Verify welcome email was sent
    mock_welcome_email.assert_called_once_with(user_id=user.id)
```

**Step 3: Run tests**

```bash
uv run pytest apps/api/tests/test_auth_views.py::TestRegisterView -v
```
Expected: PASS

**Step 4: Commit**

```bash
git add apps/api/auth_views.py apps/api/tests/test_auth_views.py
git commit -m "feat: send welcome email after registration"
```

---

## Task 10: Wire Up Password Change to Send Notification

**Files:**
- Modify: `apps/api/settings_views.py`

**Step 1: Update password change view**

In `apps/api/settings_views.py` in `ChangePasswordView.post` method, after line 208 (`log_security_event('PASSWORD_CHANGE', user, request)`), add:

```python
        # Send password changed notification email
        from apps.accounts.tasks import send_password_changed_email_async
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        send_password_changed_email_async.delay(
            user_id=user.id,
            ip_address=ip_address
        )
```

**Step 2: Update password change test**

In `apps/api/tests/test_settings_views.py`, update password change test to verify email:

```python
from unittest.mock import patch

@patch('apps.api.settings_views.send_password_changed_email_async.delay')
def test_change_password_success(self, mock_email, authenticated_client, user):
    """Test successful password change sends notification."""
    # ... existing test code ...

    # Verify notification email was sent
    mock_email.assert_called_once()
```

**Step 3: Run tests**

```bash
uv run pytest apps/api/tests/test_settings_views.py::TestChangePasswordView -v
```
Expected: PASS

**Step 4: Commit**

```bash
git add apps/api/settings_views.py apps/api/tests/test_settings_views.py
git commit -m "feat: send notification email after password change"
```

---

## Task 11: Wire Up Account Deletion to Send Email

**Files:**
- Modify: `apps/api/settings_views.py`

**Step 1: Update account deletion view**

In `apps/api/settings_views.py` in `DeleteAccountView.post` method, before line 289 (`log_security_event('ACCOUNT_DELETION', request.user, request)`), add:

```python
        # Store email and username before deletion
        user_email = request.user.email
        username = request.user.username
```

Then after line 292 (`serializer.save()`), add:

```python
        # Send account deletion confirmation email
        from apps.accounts.tasks import send_account_deleted_email_async
        send_account_deleted_email_async.delay(
            email=user_email,
            username=username
        )
```

**Step 2: Update account deletion test**

In `apps/api/tests/test_settings_views.py`, update deletion test:

```python
@patch('apps.api.settings_views.send_account_deleted_email_async.delay')
def test_delete_account_success(self, mock_email, authenticated_client, user):
    """Test successful account deletion sends confirmation email."""
    # ... existing test code ...

    # Verify confirmation email was sent
    mock_email.assert_called_once()
```

**Step 3: Run tests**

```bash
uv run pytest apps/api/tests/test_settings_views.py::TestDeleteAccountView -v
```
Expected: PASS

**Step 4: Commit**

```bash
git add apps/api/settings_views.py apps/api/tests/test_settings_views.py
git commit -m "feat: send confirmation email after account deletion"
```

---

## Task 12: Update Development Settings for Email Backend

**Files:**
- Modify: `config/settings/development.py`

**Step 1: Add console email backend fallback for development**

Add to `config/settings/development.py` after line 40 (after AXES_ENABLED):

```python
# Email backend override for development
# Use console backend instead of Resend to avoid API costs during development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Override Resend requirement for development
RESEND_API_KEY = os.getenv('RESEND_API_KEY', 'dev_key_not_required')
```

**Step 2: Commit**

```bash
git add config/settings/development.py
git commit -m "chore: use console email backend for development"
```

---

## Task 13: Add PasswordResetToken to Admin

**Files:**
- Modify: `apps/accounts/admin.py`

**Step 1: Register PasswordResetToken in admin**

Add to `apps/accounts/admin.py` after EmailChangeRequest admin:

```python


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin interface for password reset tokens."""

    list_display = ['user', 'created_at', 'expires_at', 'is_used', 'used_at']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'created_at', 'used_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Token Details', {
            'fields': ('token', 'created_at', 'expires_at')
        }),
        ('Status', {
            'fields': ('is_used', 'used_at')
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation of tokens."""
        return False
```

And add import at top:
```python
from apps.accounts.models import User, EmailChangeRequest, PasswordResetToken
```

**Step 2: Commit**

```bash
git add apps/accounts/admin.py
git commit -m "feat: add PasswordResetToken to admin interface"
```

---

## Task 14: Install Dependencies and Run Integration Tests

**Step 1: Install Resend package**

```bash
uv pip install resend==2.5.1
```

**Step 2: Run all tests**

```bash
uv run pytest -v --cov=apps
```
Expected: All tests pass with coverage > 80%

**Step 3: Test email sending manually (optional)**

Start development server:
```bash
make dev
```

Try registering a new user and check console for welcome email output.

**Step 4: Commit**

```bash
git add requirements/base.txt uv.lock
git commit -m "chore: install Resend SDK"
```

---

## Task 15: Update Documentation

**Files:**
- Create: `docs/EMAIL_BACKEND.md`
- Modify: `README.md`

**Step 1: Create email backend documentation**

Create `docs/EMAIL_BACKEND.md`:
```markdown
# Email Backend Documentation

## Overview

QuietPage uses Resend as the email service provider for all transactional emails. Emails are sent asynchronously via Celery tasks to avoid blocking HTTP requests.

## Email Types

### 1. Welcome Email
- **Trigger:** User registration
- **Template:** `templates/accounts/emails/welcome.txt`
- **Task:** `send_welcome_email_async`
- **Recipient:** New user's email

### 2. Password Reset Request
- **Trigger:** User clicks "Forgot password?"
- **Template:** `templates/accounts/emails/password_reset_request.txt`
- **Task:** `send_password_reset_email_async`
- **Token:** 1-hour expiration, single-use
- **Recipient:** User's email

### 3. Password Changed Notification
- **Trigger:** User changes password
- **Template:** `templates/accounts/emails/password_changed.txt`
- **Task:** `send_password_changed_email_async`
- **Recipient:** User's email

### 4. Email Change Verification
- **Trigger:** User requests email change
- **Template:** `templates/accounts/emails/email_verification.txt`
- **Task:** `send_email_change_verification_async`
- **Token:** 24-hour expiration
- **Recipient:** New email address

### 5. Email Changed Notification
- **Trigger:** Email change verified
- **Template:** `templates/accounts/emails/email_changed_notification.txt`
- **Task:** `send_email_changed_notification_async`
- **Recipient:** Old email address (security notification)

### 6. Account Deleted Confirmation
- **Trigger:** User deletes account
- **Template:** `templates/accounts/emails/account_deleted.txt`
- **Task:** `send_account_deleted_email_async`
- **Recipient:** User's email

## Configuration

### Environment Variables

```bash
# Required for production
RESEND_API_KEY=re_your_api_key_here
DEFAULT_FROM_EMAIL=info@quietpage.app
```

### Development

Development uses Django's console backend to print emails to terminal:

```python
# config/settings/development.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production

Production uses Resend backend:

```python
# config/settings/base.py
EMAIL_BACKEND = 'apps.core.backends.resend_backend.ResendEmailBackend'
```

## Testing Emails

### Manual Testing (Development)

1. Start development server: `make dev`
2. Register a new user
3. Check terminal output for welcome email content

### Automated Testing

```bash
# Test email backend
uv run pytest apps/core/tests/test_resend_backend.py -v

# Test email tasks
uv run pytest apps/accounts/tests/test_email_tasks.py -v

# Test email integration
uv run pytest apps/api/tests/test_password_reset_views.py -v
```

## Rate Limiting

Password reset and email change are rate limited to prevent abuse:

- Password reset: 5 requests per hour per IP
- Email change: 3 requests per hour per user

## Security

- All reset/verification tokens are cryptographically signed
- Tokens have short expiration windows (1 hour for password, 24 hours for email)
- Tokens are single-use only
- Email enumeration is prevented (always returns success)
- All security events are logged

## Troubleshooting

### Emails not sending in production

1. Check Resend API key is set: `echo $RESEND_API_KEY`
2. Check Celery is running: `celery -A config inspect active`
3. Check logs: `tail -f logs/django.log | grep email`
4. Verify domain in Resend dashboard

### Task retry failures

Emails are retried 3 times with exponential backoff (60s, 120s, 240s). Check Celery logs for failure details.

## API Endpoints

### Password Reset

```bash
# Request reset
POST /api/v1/auth/password-reset/request/
{
  "email": "user@example.com"
}

# Confirm reset
POST /api/v1/auth/password-reset/confirm/
{
  "token": "...",
  "new_password": "...",
  "new_password_confirm": "..."
}
```

### Email Change

```bash
# Request change
POST /api/v1/settings/security/email/
{
  "new_email": "new@example.com",
  "password": "current_password"
}

# Verify change
GET /api/v1/auth/email-change/verify/<token>/
```
```

**Step 2: Update README**

Add to `README.md` in the Features section:
```markdown
- **Email Notifications**: Transactional emails via Resend (welcome, password reset, security notifications)
```

**Step 3: Commit**

```bash
git add docs/EMAIL_BACKEND.md README.md
git commit -m "docs: add email backend documentation"
```

---

## Final Steps

### Review Checklist

- [ ] All tests pass (`uv run pytest -v`)
- [ ] Coverage > 80% (`uv run pytest --cov=apps`)
- [ ] No linting errors
- [ ] Environment variables documented in `.env.example`
- [ ] All email templates created
- [ ] Admin interfaces registered
- [ ] Rate limiting configured
- [ ] Security logging in place

### Deployment Checklist

1. Set `RESEND_API_KEY` in production environment
2. Verify `DEFAULT_FROM_EMAIL` domain in Resend dashboard
3. Ensure Celery workers are running
4. Ensure Redis is running (required for Celery)
5. Test password reset flow end-to-end
6. Test email change flow end-to-end
7. Monitor email delivery in Resend dashboard

---

## Notes

- All emails are in English as requested
- All emails are plain text (no HTML)
- Sender is always `info@quietpage.app`
- Development mode uses console backend (no API key needed)
- Production requires Resend API key and domain verification
- All security-sensitive actions send notification emails
- Email enumeration is prevented by always returning success

## Implementation Strategy

This plan follows TDD principles:
1. Write failing test
2. Run test to verify failure
3. Implement minimal code
4. Run test to verify success
5. Commit

Each task is independent and can be completed in 10-30 minutes. Tasks should be completed in order as they build on each other.
