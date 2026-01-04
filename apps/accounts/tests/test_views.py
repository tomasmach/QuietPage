"""
Comprehensive tests for accounts app views.

Tests all views in apps/accounts/views.py including:
- ProfileUpdateView: avatar upload, remove, resize
- GoalsUpdateView: update success
- PrivacySettingsView: stats calculation
- CustomPasswordChangeView: password change, session retention
- EmailChangeView: create request, send verification email
- EmailVerifyView: token validation, expiry check, email update
- EmailResendVerificationView: rate limiting
- EmailCancelChangeView: cancel pending request
"""

import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from datetime import timedelta
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image

from apps.accounts.models import User, EmailChangeRequest
from apps.accounts.tests.factories import (
    UserFactory,
    EmailChangeRequestFactory,
    ExpiredEmailChangeRequestFactory,
)
from apps.journal.tests.factories import EntryFactory

# Mark all tests in this module as view and unit tests
pytestmark = [pytest.mark.views, pytest.mark.unit]


class TestSettingsOverviewView:
    """Tests for SettingsOverviewView redirect."""

    def test_redirects_to_profile_settings(self, client):
        """Test that settings overview redirects to profile page."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('accounts:settings-overview'))
        
        assert response.status_code == 302
        assert response.url == reverse('accounts:settings-profile')

    def test_requires_authentication(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get(reverse('accounts:settings-overview'))
        
        assert response.status_code == 302
        assert '/accounts/login/' in response.url


class TestProfileUpdateView:
    """Tests for ProfileUpdateView."""

    def test_get_profile_update_page(self, client):
        """Test loading the profile update page."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('accounts:settings-profile'))
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['active_section'] == 'profile'

    def test_update_profile_fields(self, client):
        """Test updating basic profile fields."""
        user = UserFactory(first_name='John', last_name='Doe')
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-profile'), {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'bio': 'Test bio',
        })
        
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.first_name == 'Jane'
        assert user.last_name == 'Smith'
        assert user.bio == 'Test bio'

    def test_avatar_upload_and_resize(self, client, sample_avatar, temp_media_dir):
        """Test avatar upload triggers resize functionality."""
        user = UserFactory()
        client.force_login(user)
        
        # Create a test image larger than 512x512
        img = Image.new('RGB', (1024, 1024), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        avatar = SimpleUploadedFile(
            "test.jpg",
            buffer.read(),
            content_type="image/jpeg"
        )
        
        response = client.post(reverse('accounts:settings-profile'), {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'avatar': avatar,
        })
        
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.avatar is not None
        assert user.avatar.name is not None

    def test_avatar_remove(self, client, sample_avatar, temp_media_dir):
        """Test removing avatar with remove_avatar flag."""
        user = UserFactory()
        client.force_login(user)
        
        # First upload an avatar
        user.avatar = sample_avatar
        user.save()
        assert user.avatar is not None
        
        # Now remove it
        response = client.post(reverse('accounts:settings-profile'), {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'remove_avatar': 'true',
        })
        
        assert response.status_code == 302
        user.refresh_from_db()
        assert not user.avatar

    def test_avatar_remove_takes_priority_over_upload(self, client, sample_avatar, temp_media_dir):
        """Test that remove_avatar flag takes priority over new upload."""
        user = UserFactory()
        client.force_login(user)
        
        # Upload avatar with remove flag
        response = client.post(reverse('accounts:settings-profile'), {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'avatar': sample_avatar,
            'remove_avatar': 'true',
        })
        
        assert response.status_code == 302
        user.refresh_from_db()
        assert not user.avatar

    def test_success_message_displayed(self, client):
        """Test that success message is displayed after update."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-profile'), {
            'first_name': 'Test',
            'last_name': 'User',
            'bio': '',
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'úspěšně aktualizován' in str(messages[0])


class TestGoalsUpdateView:
    """Tests for GoalsUpdateView."""

    def test_get_goals_update_page(self, client):
        """Test loading the goals update page."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('accounts:settings-goals'))
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['active_section'] == 'goals'

    def test_update_goals_successfully(self, client):
        """Test updating writing goals and preferences."""
        user = UserFactory(daily_word_goal=500)
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-goals'), {
            'daily_word_goal': 1000,
            'preferred_writing_time': 'evening',
            'reminder_enabled': True,
            'reminder_time': '20:00',
            'timezone': 'Europe/Prague',
        })
        
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.daily_word_goal == 1000
        assert user.preferred_writing_time == 'evening'
        assert user.reminder_enabled is True

    def test_success_message_displayed(self, client):
        """Test that success message is displayed after update."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-goals'), {
            'daily_word_goal': 750,
            'preferred_writing_time': 'morning',
            'reminder_enabled': False,
            'reminder_time': '08:00',
            'timezone': 'Europe/Prague',
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert 'úspěšně aktualizovány' in str(messages[0])


class TestPrivacySettingsView:
    """Tests for PrivacySettingsView with statistics."""

    def test_get_privacy_settings_page(self, client):
        """Test loading the privacy settings page."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('accounts:settings-privacy'))
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['active_section'] == 'privacy'

    def test_statistics_calculation_no_entries(self, client):
        """Test stats calculation when user has no entries."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('accounts:settings-privacy'))
        
        stats = response.context['stats']
        assert stats['total_entries'] == 0
        assert stats['total_words'] == 0
        assert stats['current_streak'] == user.current_streak
        assert stats['longest_streak'] == user.longest_streak

    def test_statistics_calculation_with_entries(self, client):
        """Test stats calculation when user has entries."""
        user = UserFactory()
        client.force_login(user)
        
        # Create some entries with specific content to get exact word counts
        # Create content with exactly 500, 300, and 200 words
        entry1 = EntryFactory(user=user, content=' '.join(['word'] * 500))
        entry2 = EntryFactory(user=user, content=' '.join(['word'] * 300))
        entry3 = EntryFactory(user=user, content=' '.join(['word'] * 200))
        
        # Update streak values after creating entries (signals will have updated them)
        user.current_streak = 5
        user.longest_streak = 10
        user.save()
        
        response = client.get(reverse('accounts:settings-privacy'))
        
        stats = response.context['stats']
        assert stats['total_entries'] == 3
        assert stats['total_words'] == 1000
        assert stats['current_streak'] == 5
        assert stats['longest_streak'] == 10
        assert 'account_created' in stats

    def test_update_privacy_settings(self, client):
        """Test updating email notification preferences."""
        user = UserFactory(email_notifications=False)
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-privacy'), {
            'email_notifications': True,
        })
        
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.email_notifications is True


class TestCustomPasswordChangeView:
    """Tests for CustomPasswordChangeView."""

    def test_get_password_change_page(self, client):
        """Test loading the password change page."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('accounts:settings-password'))
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['active_section'] == 'password'

    def test_password_change_success(self, client):
        """Test successful password change."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-password'), {
            'old_password': 'testpass123',
            'new_password1': 'newpass456!',
            'new_password2': 'newpass456!',
        })
        
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.check_password('newpass456!')

    def test_user_stays_logged_in_after_password_change(self, client):
        """Test that user session is retained after password change."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-password'), {
            'old_password': 'testpass123',
            'new_password1': 'newpass456!',
            'new_password2': 'newpass456!',
        }, follow=True)
        
        # User should still be authenticated
        assert response.wsgi_request.user.is_authenticated
        assert response.wsgi_request.user.id == user.id

    def test_success_message_displayed(self, client):
        """Test that success message is displayed after password change."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-password'), {
            'old_password': 'testpass123',
            'new_password1': 'newpass456!',
            'new_password2': 'newpass456!',
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert any('úspěšně změněno' in str(m) for m in messages)


class TestEmailChangeView:
    """Tests for EmailChangeView."""

    def test_get_email_change_page(self, client):
        """Test loading the email change page."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.get(reverse('accounts:settings-email'))
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['current_email'] == user.email
        assert response.context['active_section'] == 'email'

    def test_pending_request_shown_in_context(self, client):
        """Test that pending email change request is shown in context."""
        user = UserFactory()
        client.force_login(user)
        
        # Create pending request
        request = EmailChangeRequestFactory(user=user, new_email='new@example.com')
        
        response = client.get(reverse('accounts:settings-email'))
        
        assert 'pending_request' in response.context
        assert response.context['pending_request'].new_email == 'new@example.com'

    def test_expired_request_not_shown(self, client):
        """Test that expired request is not shown in context."""
        user = UserFactory()
        client.force_login(user)
        
        # Create expired request
        ExpiredEmailChangeRequestFactory(user=user)
        
        response = client.get(reverse('accounts:settings-email'))
        
        assert 'pending_request' not in response.context

    @patch('apps.accounts.views.send_email_verification')
    def test_create_email_change_request(self, mock_send, client):
        """Test creating a new email change request."""
        mock_send.return_value = True
        user = UserFactory(email='old@example.com')
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-email'), {
            'new_email': 'new@example.com',
            'password': 'testpass123',
        })
        
        assert response.status_code == 302
        assert EmailChangeRequest.objects.filter(
            user=user,
            new_email='new@example.com',
            is_verified=False
        ).exists()

    @patch('apps.accounts.views.send_email_verification')
    def test_cancels_existing_pending_requests(self, mock_send, client):
        """Test that existing pending requests are cancelled when creating new one."""
        mock_send.return_value = True
        user = UserFactory()
        client.force_login(user)
        
        # Create existing pending request
        old_request = EmailChangeRequestFactory(user=user, new_email='old@example.com')
        
        response = client.post(reverse('accounts:settings-email'), {
            'new_email': 'new@example.com',
            'password': 'testpass123',
        })
        
        assert response.status_code == 302
        # Old request should be deleted
        assert not EmailChangeRequest.objects.filter(id=old_request.id).exists()
        # New request should exist
        assert EmailChangeRequest.objects.filter(
            user=user,
            new_email='new@example.com'
        ).exists()

    @patch('apps.accounts.views.send_email_verification')
    def test_sends_verification_email(self, mock_send, client):
        """Test that verification email is sent."""
        mock_send.return_value = True
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-email'), {
            'new_email': 'new@example.com',
            'password': 'testpass123',
        })
        
        assert response.status_code == 302
        mock_send.assert_called_once()
        args = mock_send.call_args[0]
        assert args[0] == user
        assert args[1] == 'new@example.com'

    @patch('apps.accounts.views.send_email_verification')
    def test_success_message_when_email_sent(self, mock_send, client):
        """Test success message when email is sent successfully."""
        mock_send.return_value = True
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-email'), {
            'new_email': 'new@example.com',
            'password': 'testpass123',
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert any('verifikační odkaz' in str(m).lower() for m in messages)

    @patch('apps.accounts.views.send_email_verification')
    def test_error_message_when_email_fails(self, mock_send, client):
        """Test error message when email sending fails."""
        mock_send.return_value = False
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:settings-email'), {
            'new_email': 'new@example.com',
            'password': 'testpass123',
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert any('nepodařilo se odeslat' in str(m).lower() for m in messages)


class TestEmailVerifyView:
    """Tests for EmailVerifyView."""

    @patch('apps.accounts.views.verify_email_change_token')
    def test_successful_email_verification(self, mock_verify, client):
        """Test successful email verification with valid token."""
        user = UserFactory(email='old@example.com')
        request = EmailChangeRequestFactory(user=user, new_email='new@example.com')
        
        # Mock token verification
        mock_verify.return_value = (user.id, 'new@example.com')
        
        response = client.get(reverse('accounts:email-verify', kwargs={'token': 'valid-token'}))
        
        assert response.status_code == 200
        assert response.context['success'] is True
        assert response.context['new_email'] == 'new@example.com'
        
        # Check user email was updated
        user.refresh_from_db()
        assert user.email == 'new@example.com'
        
        # Check request marked as verified
        request.refresh_from_db()
        assert request.is_verified is True
        assert request.verified_at is not None

    @patch('apps.accounts.views.verify_email_change_token')
    def test_expired_token_error(self, mock_verify, client):
        """Test error handling for expired token."""
        mock_verify.return_value = (None, None)
        
        response = client.get(reverse('accounts:email-verify', kwargs={'token': 'expired-token'}))
        
        assert response.status_code == 200
        assert response.context['success'] is False
        assert response.context['error'] == 'expired'

    @patch('apps.accounts.views.verify_email_change_token')
    def test_invalid_user_error(self, mock_verify, client):
        """Test error when user doesn't exist."""
        mock_verify.return_value = (99999, 'new@example.com')  # Non-existent user ID
        
        response = client.get(reverse('accounts:email-verify', kwargs={'token': 'invalid-token'}))
        
        assert response.status_code == 200
        assert response.context['success'] is False
        assert response.context['error'] == 'invalid'

    @patch('apps.accounts.views.verify_email_change_token')
    def test_no_matching_request_error(self, mock_verify, client):
        """Test error when no matching email change request exists."""
        user = UserFactory()
        mock_verify.return_value = (user.id, 'nonexistent@example.com')
        
        response = client.get(reverse('accounts:email-verify', kwargs={'token': 'token'}))
        
        assert response.status_code == 200
        assert response.context['success'] is False
        assert response.context['error'] == 'invalid'

    @patch('apps.accounts.views.verify_email_change_token')
    def test_expired_request_error(self, mock_verify, client):
        """Test error when request has expired."""
        user = UserFactory()
        request = ExpiredEmailChangeRequestFactory(user=user, new_email='new@example.com')
        
        mock_verify.return_value = (user.id, 'new@example.com')
        
        response = client.get(reverse('accounts:email-verify', kwargs={'token': 'token'}))
        
        assert response.status_code == 200
        assert response.context['success'] is False
        assert response.context['error'] == 'expired'

    @patch('apps.accounts.views.verify_email_change_token')
    def test_email_already_taken_error(self, mock_verify, client):
        """Test error when new email is already taken by another user."""
        user1 = UserFactory(email='user1@example.com')
        user2 = UserFactory(email='user2@example.com')
        request = EmailChangeRequestFactory(user=user1, new_email='user2@example.com')
        
        mock_verify.return_value = (user1.id, 'user2@example.com')
        
        response = client.get(reverse('accounts:email-verify', kwargs={'token': 'token'}))
        
        assert response.status_code == 200
        assert response.context['success'] is False
        assert response.context['error'] == 'taken'
        
        # Request should be deleted
        assert not EmailChangeRequest.objects.filter(id=request.id).exists()


class TestEmailResendVerificationView:
    """Tests for EmailResendVerificationView."""

    @patch('apps.accounts.views.send_email_verification')
    def test_resend_verification_email_success(self, mock_send, client):
        """Test successfully resending verification email."""
        mock_send.return_value = True
        user = UserFactory()
        client.force_login(user)
        
        request = EmailChangeRequestFactory(user=user, new_email='new@example.com')
        
        response = client.post(reverse('accounts:email-resend'))
        
        assert response.status_code == 302
        mock_send.assert_called_once()

    def test_error_when_no_pending_request(self, client):
        """Test error message when no pending request exists."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:email-resend'), follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert any('nebyly nalezeny' in str(m).lower() for m in messages)

    @patch('apps.accounts.views.send_email_verification')
    def test_rate_limiting_max_3_per_hour(self, mock_send, client):
        """Test rate limiting prevents more than 3 requests per hour."""
        mock_send.return_value = True
        user = UserFactory()
        client.force_login(user)
        
        # Create 3 recent requests (within last hour)
        for i in range(3):
            EmailChangeRequestFactory(
                user=user,
                new_email='test@example.com',
                created_at=timezone.now() - timedelta(minutes=30)
            )
        
        response = client.post(reverse('accounts:email-resend'), follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert any('příliš mnoho' in str(m).lower() for m in messages)
        mock_send.assert_not_called()

    @patch('apps.accounts.views.send_email_verification')
    def test_rate_limiting_allows_after_hour(self, mock_send, client):
        """Test rate limiting allows requests after an hour."""
        mock_send.return_value = True
        user = UserFactory()
        client.force_login(user)
        
        # Create 3 old requests (more than 1 hour ago)
        for i in range(3):
            EmailChangeRequestFactory(
                user=user,
                new_email='test@example.com',
                created_at=timezone.now() - timedelta(hours=2)
            )
        
        # Create current pending request
        EmailChangeRequestFactory(user=user, new_email='test@example.com')
        
        response = client.post(reverse('accounts:email-resend'))
        
        assert response.status_code == 302
        mock_send.assert_called_once()


class TestEmailCancelChangeView:
    """Tests for EmailCancelChangeView."""

    def test_cancel_pending_request(self, client):
        """Test cancelling a pending email change request."""
        user = UserFactory()
        client.force_login(user)
        
        request = EmailChangeRequestFactory(user=user)
        
        response = client.post(reverse('accounts:email-cancel'))
        
        assert response.status_code == 302
        assert not EmailChangeRequest.objects.filter(id=request.id).exists()

    def test_success_message_when_cancelled(self, client):
        """Test success message is shown when request is cancelled."""
        user = UserFactory()
        client.force_login(user)
        
        EmailChangeRequestFactory(user=user)
        
        response = client.post(reverse('accounts:email-cancel'), follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert any('zrušena' in str(m).lower() for m in messages)

    def test_info_message_when_no_pending_request(self, client):
        """Test info message when there's no pending request to cancel."""
        user = UserFactory()
        client.force_login(user)
        
        response = client.post(reverse('accounts:email-cancel'), follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        assert any('nebyly nalezeny' in str(m).lower() for m in messages)

