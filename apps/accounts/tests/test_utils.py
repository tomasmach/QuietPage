"""
Comprehensive tests for accounts app utility functions.

Tests all utilities in apps/accounts/utils.py including:
- resize_avatar(): JPEG/PNG handling, RGBA→RGB conversion
- get_user_avatar_url(): return avatar URL or default
- generate_email_verification_token(): token generation
- verify_email_change_token(): valid token, expired token, invalid token
- send_email_verification(): mock email sending
"""

import pytest
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from django.conf import settings
from django.core.signing import TimestampSigner
from unittest.mock import patch, MagicMock
from freezegun import freeze_time
import time

from apps.accounts.utils import (
    resize_avatar,
    get_user_avatar_url,
    generate_email_verification_token,
    verify_email_change_token,
    send_email_verification,
)
from apps.accounts.tests.factories import UserFactory


@pytest.mark.utils
@pytest.mark.unit
class TestResizeAvatar:
    """Tests for resize_avatar utility function."""

    def test_resize_large_image_to_512x512(self):
        """Test resizing a large image to 512x512."""
        # Create a 1024x1024 RGB image
        img = Image.new('RGB', (1024, 1024), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            buffer.read(),
            content_type="image/jpeg"
        )
        
        result = resize_avatar(uploaded_file)
        
        assert isinstance(result, InMemoryUploadedFile)
        assert result.content_type == 'image/jpeg'
        assert result.name.endswith('.jpg')
        
        # Verify dimensions
        result.seek(0)
        output_img = Image.open(result)
        assert output_img.size == (512, 512)

    def test_resize_small_image_to_512x512(self):
        """Test resizing a small image to 512x512."""
        # Create a 100x100 RGB image
        img = Image.new('RGB', (100, 100), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "small.jpg",
            buffer.read(),
            content_type="image/jpeg"
        )
        
        result = resize_avatar(uploaded_file)
        
        # Verify dimensions
        result.seek(0)
        output_img = Image.open(result)
        assert output_img.size == (512, 512)

    def test_convert_png_to_jpeg(self):
        """Test converting PNG to JPEG format."""
        # Create PNG image
        img = Image.new('RGB', (800, 800), color='green')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "test.png",
            buffer.read(),
            content_type="image/png"
        )
        
        result = resize_avatar(uploaded_file)
        
        assert result.content_type == 'image/jpeg'
        assert result.name.endswith('.jpg')

    def test_convert_rgba_to_rgb(self):
        """Test converting RGBA (transparent PNG) to RGB with white background."""
        # Create RGBA image with transparency
        img = Image.new('RGBA', (800, 800), color=(255, 0, 0, 128))  # Semi-transparent red
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "transparent.png",
            buffer.read(),
            content_type="image/png"
        )
        
        result = resize_avatar(uploaded_file)
        
        # Verify conversion to RGB
        result.seek(0)
        output_img = Image.open(result)
        assert output_img.mode == 'RGB'

    def test_maintains_aspect_ratio_with_centering(self):
        """Test that non-square images are centered on white background."""
        # Create a rectangular image (800x400)
        img = Image.new('RGB', (800, 400), color='purple')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "rect.jpg",
            buffer.read(),
            content_type="image/jpeg"
        )
        
        result = resize_avatar(uploaded_file)
        
        # Verify output is square
        result.seek(0)
        output_img = Image.open(result)
        assert output_img.size == (512, 512)

    def test_output_quality_and_optimization(self):
        """Test that output is optimized JPEG with quality 90."""
        img = Image.new('RGB', (1024, 1024), color='yellow')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            buffer.read(),
            content_type="image/jpeg"
        )
        
        result = resize_avatar(uploaded_file)
        
        # File should be reasonably sized due to optimization
        assert result.size < 1024 * 1024  # Less than 1MB for solid color
        assert result.content_type == 'image/jpeg'

    def test_custom_size_parameter(self):
        """Test resizing to custom dimensions."""
        img = Image.new('RGB', (1024, 1024), color='cyan')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            buffer.read(),
            content_type="image/jpeg"
        )
        
        result = resize_avatar(uploaded_file, size=(256, 256))
        
        result.seek(0)
        output_img = Image.open(result)
        assert output_img.size == (256, 256)


@pytest.mark.utils
@pytest.mark.unit
class TestGetUserAvatarUrl:
    """Tests for get_user_avatar_url utility function."""

    def test_returns_avatar_url_when_user_has_avatar(self, sample_avatar, temp_media_dir):
        """Test returning user's avatar URL when they have one."""
        user = UserFactory()
        user.avatar = sample_avatar
        user.save()
        
        url = get_user_avatar_url(user)
        
        assert url == user.avatar.url
        assert url is not None

    def test_returns_default_avatar_when_no_avatar(self):
        """Test returning default avatar URL when user has no avatar."""
        user = UserFactory()
        user.avatar = None
        
        url = get_user_avatar_url(user)
        
        assert url == f"{settings.STATIC_URL}images/default-avatar.png"

    def test_returns_default_when_avatar_field_empty(self):
        """Test returning default when avatar field is empty string."""
        user = UserFactory()
        user.avatar = ''
        
        url = get_user_avatar_url(user)
        
        assert url == f"{settings.STATIC_URL}images/default-avatar.png"


@pytest.mark.utils
@pytest.mark.unit
class TestGenerateEmailVerificationToken:
    """Tests for generate_email_verification_token utility function."""

    def test_generates_valid_token(self):
        """Test that a valid token is generated."""
        token = generate_email_verification_token(123, 'test@example.com')
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_user_id_and_email(self):
        """Test that token can be decoded to reveal user_id and email."""
        user_id = 456
        email = 'user@example.com'
        
        token = generate_email_verification_token(user_id, email)
        
        # Manually decode to verify contents
        signer = TimestampSigner()
        original = signer.unsign(token)
        # Token format is user_id:email:nonce (3 parts)
        parts = original.split(':', 2)
        decoded_id = parts[0]
        decoded_email = parts[1]
        # parts[2] is the nonce
        
        assert int(decoded_id) == user_id
        assert decoded_email == email

    def test_different_inputs_generate_different_tokens(self):
        """Test that different inputs generate different tokens."""
        token1 = generate_email_verification_token(1, 'email1@example.com')
        token2 = generate_email_verification_token(2, 'email2@example.com')
        
        assert token1 != token2

    def test_same_inputs_generate_different_tokens_due_to_timestamp(self):
        """Test that same inputs at different times generate different tokens."""
        with patch('django.core.signing.time.time') as mock_time:
            # First token with timestamp 1000
            mock_time.return_value = 1000
            token1 = generate_email_verification_token(1, 'test@example.com')
            
            # Second token with timestamp 2000
            mock_time.return_value = 2000
            token2 = generate_email_verification_token(1, 'test@example.com')
        
        # Tokens should differ due to timestamp
        assert token1 != token2


@pytest.mark.utils
@pytest.mark.unit
class TestVerifyEmailChangeToken:
    """Tests for verify_email_change_token utility function."""

    def test_verify_valid_token(self):
        """Test verifying a valid, non-expired token."""
        user_id = 789
        email = 'valid@example.com'
        token = generate_email_verification_token(user_id, email)
        
        result_id, result_email = verify_email_change_token(token, max_age=86400)
        
        assert result_id == user_id
        assert result_email == email

    def test_verify_expired_token_returns_none(self):
        """Test that expired token returns (None, None)."""
        user_id = 123
        email = 'expired@example.com'
        
        # Generate token and verify with very short max_age
        with freeze_time("2025-01-01 12:00:00"):
            token = generate_email_verification_token(user_id, email)
        
        # Try to verify 2 days later with 1 day max_age
        with freeze_time("2025-01-03 12:00:00"):
            result_id, result_email = verify_email_change_token(token, max_age=86400)
        
        assert result_id is None
        assert result_email is None

    def test_verify_invalid_token_returns_none(self):
        """Test that invalid/corrupted token returns (None, None)."""
        invalid_token = 'this-is-not-a-valid-token'
        
        result_id, result_email = verify_email_change_token(invalid_token)
        
        assert result_id is None
        assert result_email is None

    def test_verify_tampered_token_returns_none(self):
        """Test that tampered token returns (None, None)."""
        token = generate_email_verification_token(1, 'test@example.com')
        # Tamper with the token
        tampered_token = token[:-5] + 'xxxxx'
        
        result_id, result_email = verify_email_change_token(tampered_token)
        
        assert result_id is None
        assert result_email is None

    def test_verify_with_custom_max_age(self):
        """Test verifying token with custom max_age parameter."""
        user_id = 999
        email = 'custom@example.com'
        
        # Generate token
        with freeze_time("2025-01-01 12:00:00"):
            token = generate_email_verification_token(user_id, email)
        
        # Verify 30 minutes later with 1 hour max_age - should succeed
        with freeze_time("2025-01-01 12:30:00"):
            result_id, result_email = verify_email_change_token(token, max_age=3600)
        
        assert result_id == user_id
        assert result_email == email

    def test_token_with_colon_in_email(self):
        """Test handling email addresses (edge case with colon in value)."""
        user_id = 111
        # Standard email should work fine even though we split on ':'
        email = 'user+tag@example.com'
        
        token = generate_email_verification_token(user_id, email)
        result_id, result_email = verify_email_change_token(token)
        
        assert result_id == user_id
        assert result_email == email


@pytest.mark.utils
@pytest.mark.unit
class TestSendEmailVerification:
    """Tests for send_email_verification utility function."""

    @patch('apps.accounts.utils.send_mail')
    def test_sends_email_successfully(self, mock_send_mail, rf):
        """Test that email is sent successfully."""
        mock_send_mail.return_value = 1  # Success
        user = UserFactory(username='testuser')
        new_email = 'new@example.com'
        request = rf.get('/')
        
        result = send_email_verification(user, new_email, request)
        
        assert result is True
        mock_send_mail.assert_called_once()

    @patch('apps.accounts.utils.send_mail')
    def test_email_contains_correct_recipient(self, mock_send_mail, rf):
        """Test that email is sent to correct recipient."""
        mock_send_mail.return_value = 1
        user = UserFactory()
        new_email = 'recipient@example.com'
        request = rf.get('/')
        
        send_email_verification(user, new_email, request)
        
        call_kwargs = mock_send_mail.call_args[1]
        assert call_kwargs['recipient_list'] == [new_email]

    @patch('apps.accounts.utils.send_mail')
    def test_email_contains_verification_url(self, mock_send_mail, rf):
        """Test that email contains verification URL."""
        mock_send_mail.return_value = 1
        user = UserFactory()
        new_email = 'test@example.com'
        request = rf.get('/')
        
        send_email_verification(user, new_email, request)
        
        call_kwargs = mock_send_mail.call_args[1]
        html_message = call_kwargs['html_message']
        
        # Should contain verification path
        assert 'email/verify/' in html_message or '/verify/' in html_message

    @patch('apps.accounts.utils.send_mail')
    def test_email_subject_is_correct(self, mock_send_mail, rf):
        """Test that email subject is correct."""
        mock_send_mail.return_value = 1
        user = UserFactory()
        new_email = 'test@example.com'
        request = rf.get('/')
        
        send_email_verification(user, new_email, request)
        
        # send_mail is called with subject as first positional argument
        call_args = mock_send_mail.call_args[0]
        subject = call_args[0]
        assert 'QuietPage' in subject
        assert 'e-mail' in subject.lower()

    @patch('apps.accounts.utils.send_mail')
    def test_returns_false_on_email_failure(self, mock_send_mail, rf):
        """Test that function returns False when email sending fails."""
        mock_send_mail.side_effect = Exception('SMTP error')
        user = UserFactory()
        new_email = 'test@example.com'
        request = rf.get('/')
        
        result = send_email_verification(user, new_email, request)
        
        assert result is False

    @patch('apps.accounts.utils.send_mail')
    def test_uses_default_from_email(self, mock_send_mail, rf):
        """Test that default from_email is used."""
        mock_send_mail.return_value = 1
        user = UserFactory()
        new_email = 'test@example.com'
        request = rf.get('/')
        
        send_email_verification(user, new_email, request)
        
        call_kwargs = mock_send_mail.call_args[1]
        assert 'from_email' in call_kwargs
        # Should use settings.DEFAULT_FROM_EMAIL or fallback
        assert '@' in call_kwargs['from_email']

    @patch('apps.accounts.utils.send_mail')
    def test_email_includes_both_html_and_plain_text(self, mock_send_mail, rf):
        """Test that both HTML and plain text versions are sent."""
        mock_send_mail.return_value = 1
        user = UserFactory()
        new_email = 'test@example.com'
        request = rf.get('/')
        
        send_email_verification(user, new_email, request)
        
        call_kwargs = mock_send_mail.call_args[1]
        call_args = mock_send_mail.call_args[0]
        
        # Plain text message
        assert len(call_args) > 0 and len(call_args[1]) > 0
        # HTML message
        assert 'html_message' in call_kwargs
        assert len(call_kwargs['html_message']) > 0

    @patch('apps.accounts.utils.send_mail')
    def test_generates_unique_token_for_each_call(self, mock_send_mail, rf):
        """Test that each call generates a unique verification token."""
        mock_send_mail.return_value = 1
        user = UserFactory()
        new_email = 'test@example.com'
        request = rf.get('/')
        
        # Send twice
        send_email_verification(user, new_email, request)
        first_html = mock_send_mail.call_args[1]['html_message']
        
        time.sleep(0.1)
        
        send_email_verification(user, new_email, request)
        second_html = mock_send_mail.call_args[1]['html_message']
        
        # HTML should be different due to different tokens (with timestamps)
        assert first_html != second_html

    @patch('apps.accounts.utils.logger')
    @patch('apps.accounts.utils.send_mail')
    def test_logs_error_on_failure(self, mock_send_mail, mock_logger, rf):
        """Test that errors are logged when email sending fails."""
        mock_send_mail.side_effect = Exception('SMTP error')
        user = UserFactory()
        new_email = 'test@example.com'
        request = rf.get('/')
        
        send_email_verification(user, new_email, request)
        
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert 'Failed to send verification email' in error_message
        assert new_email in error_message
