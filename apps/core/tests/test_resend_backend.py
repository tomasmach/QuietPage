"""Tests for Resend email backend."""

import pytest
from unittest.mock import patch, MagicMock
from django.core.mail import send_mail
from django.test import override_settings


@pytest.mark.unit
class TestResendBackend:
    """Test Resend email backend integration."""

    @override_settings(
        EMAIL_BACKEND='apps.core.backends.resend_backend.ResendEmailBackend',
        RESEND_API_KEY='test_api_key'
    )
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

    @override_settings(
        EMAIL_BACKEND='apps.core.backends.resend_backend.ResendEmailBackend',
        RESEND_API_KEY='test_api_key'
    )
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

    @override_settings(
        EMAIL_BACKEND='apps.core.backends.resend_backend.ResendEmailBackend',
        RESEND_API_KEY='test_api_key'
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
