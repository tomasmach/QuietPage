"""
Comprehensive pytest tests for settings API views.

Tests all settings API endpoints in apps/api/settings_views.py with 80%+ coverage.
"""

import json
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.signing import TimestampSigner
from django.utils import timezone
from unittest import mock

from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory

User = get_user_model()


@pytest.mark.views
@pytest.mark.unit
class TestDeleteAccountAPIView:
    """Test DeleteAccountView for account deletion."""

    def test_delete_account_success_with_SMAZAT(self, client):
        """User can delete account with correct password and 'SMAZAT' confirmation."""
        from unittest.mock import patch

        user = UserFactory()
        client.force_login(user)

        with patch('apps.accounts.tasks.send_account_deleted_email_async.delay') as mock_email:
            response = client.post(
                reverse('api:settings-delete-account'),
                data=json.dumps({'password': 'testpass123', 'confirmation_text': 'SMAZAT'}),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'uspesne smazan' in data['message'].lower()

        # Verify confirmation email was sent
        mock_email.assert_called_once()

    def test_delete_account_success_with_DELETE(self, client):
        """User can delete account with correct password and 'DELETE' confirmation."""
        user = UserFactory()
        client.force_login(user)

        response = client.post(
            reverse('api:settings-delete-account'),
            data=json.dumps({'password': 'testpass123', 'confirmation_text': 'DELETE'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data

    def test_delete_account_wrong_password(self, client):
        """Cannot delete account with wrong password."""
        user = UserFactory()
        client.force_login(user)

        response = client.post(
            reverse('api:settings-delete-account'),
            data=json.dumps({'password': 'wrongpassword', 'confirmation_text': 'SMAZAT'}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'errors' in data

    def test_delete_account_missing_confirmation(self, client):
        """Cannot delete account without confirmation text."""
        user = UserFactory()
        client.force_login(user)

        response = client.post(
            reverse('api:settings-delete-account'),
            data=json.dumps({'password': 'testpass123'}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'errors' in data

    def test_delete_account_invalid_confirmation(self, client):
        """Cannot delete account with invalid confirmation text."""
        user = UserFactory()
        client.force_login(user)

        response = client.post(
            reverse('api:settings-delete-account'),
            data=json.dumps({'password': 'testpass123', 'confirmation_text': 'INVALID'}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'errors' in data

    def test_delete_account_requires_auth(self, client):
        """Unauthenticated users cannot delete account."""
        response = client.post(
            reverse('api:settings-delete-account'),
            data=json.dumps({'password': 'testpass123', 'confirmation_text': 'SMAZAT'}),
            content_type='application/json'
        )

        assert response.status_code == 403

    def test_delete_account_cascade_deletes_entries(self, client):
        """Deleting account should cascade delete all entries."""
        from apps.journal.models import Entry
        user = UserFactory()
        EntryFactory.create_batch(5, user=user)
        entry_ids = [e.id for e in Entry.objects.filter(user=user)]

        client.force_login(user)
        response = client.post(
            reverse('api:settings-delete-account'),
            data=json.dumps({'password': 'testpass123', 'confirmation_text': 'SMAZAT'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert not User.objects.filter(id=user.id).exists()
        assert not Entry.objects.filter(id__in=entry_ids).exists()

    def test_delete_account_logs_out_user(self, client):
        """After deleting account, user should be logged out."""
        user = UserFactory()
        client.force_login(user)

        response = client.post(
            reverse('api:settings-delete-account'),
            data=json.dumps({'password': 'testpass123', 'confirmation_text': 'SMAZAT'}),
            content_type='application/json'
        )

        assert response.status_code == 200

        response = client.get(reverse('api:settings-profile'))
        assert response.status_code == 403


@pytest.mark.views
@pytest.mark.unit
class TestProfileSettingsAPIView:
    """Test ProfileSettingsView for profile settings."""

    def test_get_profile_settings(self, client):
        """User can retrieve their profile settings."""
        user = UserFactory(bio='Test bio')
        client.force_login(user)

        response = client.get(reverse('api:settings-profile'))

        assert response.status_code == 200
        data = response.json()
        assert data['bio'] == 'Test bio'

    def test_patch_profile_update(self, client):
        """User can update their profile settings."""
        user = UserFactory()
        client.force_login(user)

        response = client.patch(
            reverse('api:settings-profile'),
            data=json.dumps({'bio': 'New bio'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.bio == 'New bio'

    def test_patch_profile_update_partial(self, client):
        """User can update partial profile fields."""
        user = UserFactory()
        client.force_login(user)

        response = client.patch(
            reverse('api:settings-profile'),
            data=json.dumps({'bio': 'New bio'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.bio == 'New bio'

    def test_profile_requires_auth(self, client):
        """Unauthenticated users cannot access profile settings."""
        response = client.get(reverse('api:settings-profile'))
        assert response.status_code == 403

        response = client.patch(
            reverse('api:settings-profile'),
            data=json.dumps({'bio': 'Test'}),
            content_type='application/json'
        )
        assert response.status_code == 403


@pytest.mark.views
@pytest.mark.unit
class TestGoalsSettingsAPIView:
    """Test GoalsSettingsView for goals settings."""

    def test_get_goals_settings(self, client):
        """User can retrieve their goals settings."""
        user = UserFactory(daily_word_goal=500, timezone='Europe/Prague')
        client.force_login(user)

        response = client.get(reverse('api:settings-goals'))

        assert response.status_code == 200
        data = response.json()
        assert data['daily_word_goal'] == 500
        assert data['timezone'] == 'Europe/Prague'

    def test_patch_goals_update(self, client):
        """User can update their goals settings."""
        user = UserFactory(daily_word_goal=500)
        client.force_login(user)

        response = client.patch(
            reverse('api:settings-goals'),
            data=json.dumps({'daily_word_goal': 1000, 'timezone': 'America/New_York'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.daily_word_goal == 1000
        assert str(user.timezone) == 'America/New_York'

    def test_patch_goals_invalid_daily_word_goal_too_low(self, client):
        """Cannot set daily_word_goal below 100."""
        user = UserFactory()
        client.force_login(user)

        response = client.patch(
            reverse('api:settings-goals'),
            data=json.dumps({'daily_word_goal': 50}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'errors' in data

    def test_patch_goals_invalid_timezone(self, client):
        """Cannot set invalid timezone."""
        user = UserFactory()
        client.force_login(user)

        response = client.patch(
            reverse('api:settings-goals'),
            data=json.dumps({'timezone': 'Invalid/Timezone'}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'errors' in data


@pytest.mark.views
@pytest.mark.unit
class TestPrivacySettingsAPIView:
    """Test PrivacySettingsView for privacy settings."""

    def test_get_privacy_settings(self, client):
        """User can retrieve their privacy settings."""
        user = UserFactory(email_notifications=True)
        client.force_login(user)

        response = client.get(reverse('api:settings-privacy'))

        assert response.status_code == 200
        data = response.json()
        assert data['email_notifications'] is True

    def test_patch_privacy_update(self, client):
        """User can update their privacy settings."""
        user = UserFactory(email_notifications=True)
        client.force_login(user)

        response = client.patch(
            reverse('api:settings-privacy'),
            data=json.dumps({'email_notifications': False}),
            content_type='application/json'
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email_notifications is False

    def test_privacy_requires_auth(self, client):
        """Unauthenticated users cannot access privacy settings."""
        response = client.get(reverse('api:settings-privacy'))
        assert response.status_code == 403

        response = client.patch(
            reverse('api:settings-privacy'),
            data=json.dumps({'email_notifications': False}),
            content_type='application/json'
        )
        assert response.status_code == 403


@pytest.mark.views
@pytest.mark.unit
class TestChangePasswordAPIView:
    """Test ChangePasswordView for password change."""

    def test_change_password_success(self, client):
        """User can change password successfully."""
        from unittest.mock import patch

        user = UserFactory()
        client.force_login(user)

        with patch('apps.accounts.tasks.send_password_changed_email_async.delay') as mock_email:
            response = client.post(
                reverse('api:settings-change-password'),
                data=json.dumps({
                    'current_password': 'testpass123',
                    'new_password': 'NewPass123!',
                    'new_password_confirm': 'NewPass123!'
                }),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'uspesne zmeneno' in data['message'].lower()

        # Verify notification email was sent
        mock_email.assert_called_once()
        # Verify it was called with correct arguments
        call_kwargs = mock_email.call_args.kwargs
        assert call_kwargs['user_id'] == user.id
        assert 'ip_address' in call_kwargs

    def test_change_password_wrong_current(self, client):
        """Cannot change password with wrong current password."""
        user = UserFactory()
        client.force_login(user)

        response = client.post(
            reverse('api:settings-change-password'),
            data=json.dumps({
                'current_password': 'wrongpassword',
                'new_password': 'NewPass123!',
                'new_password_confirm': 'NewPass123!'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'errors' in data

    def test_change_password_mismatch(self, client):
        """Cannot change password when new passwords don't match."""
        user = UserFactory()
        client.force_login(user)

        response = client.post(
            reverse('api:settings-change-password'),
            data=json.dumps({
                'current_password': 'testpass123',
                'new_password': 'NewPass123!',
                'new_password_confirm': 'DifferentPass123!'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'errors' in data


@pytest.mark.views
@pytest.mark.unit
@pytest.mark.django_db
class TestChangeEmailAPIView:
    """Test ChangeEmailView for email change."""

    def test_change_email_success(self, client, settings):
        """User can request email change successfully."""
        from apps.accounts.models import EmailChangeRequest
        from unittest.mock import patch

        # Ensure throttle rate is set for this test
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['email_change'] = '3/hour'

        user = UserFactory(email='old@example.com')
        client.force_login(user)

        with patch('apps.accounts.tasks.send_email_change_verification_async.delay'):
            response = client.post(
                reverse('api:settings-change-email'),
                data=json.dumps({
                    'new_email': 'new@example.com',
                    'password': 'testpass123'
                }),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'Verification email sent' in data['message']

        # Email should NOT be changed yet (requires verification)
        user.refresh_from_db()
        assert user.email == 'old@example.com'

        # Verify EmailChangeRequest was created
        email_request = EmailChangeRequest.objects.filter(user=user, new_email='new@example.com').first()
        assert email_request is not None
        assert email_request.is_verified is False

    def test_change_email_already_taken(self, client, settings):
        """Cannot change email to one already taken by another user."""
        # Ensure throttle rate is set for this test
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['email_change'] = '3/hour'

        user1 = UserFactory(email='user1@example.com')
        user2 = UserFactory(email='user2@example.com')
        client.force_login(user1)

        response = client.post(
            reverse('api:settings-change-email'),
            data=json.dumps({
                'new_email': 'user2@example.com',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'errors' in data

    def test_change_email_same_as_current(self, client, settings):
        """Cannot change email to the same email."""
        # Ensure throttle rate is set for this test
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['email_change'] = '3/hour'

        user = UserFactory(email='test@example.com')
        client.force_login(user)

        response = client.post(
            reverse('api:settings-change-email'),
            data=json.dumps({
                'new_email': 'test@example.com',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'errors' in data


@pytest.mark.views
@pytest.mark.unit
class TestExportDownloadAPIView:
    """Test ExportDownloadView for secure export downloads."""

    @pytest.fixture
    def create_export_file(self):
        """Fixture to create a test export file in storage with UUID-based filename."""
        import uuid
        created_paths = []

        def _create_file(user_id, use_uuid=True):
            if use_uuid:
                # New UUID-based format for security
                unique_id = uuid.uuid4()
                filename = f'user_{user_id}_{unique_id}.json'
            else:
                # Old timestamp format (for testing backward compatibility/rejection)
                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                filename = f'user_{user_id}_export_{timestamp}.json'

            storage_path = f'exports/{filename}'

            # Create test export data
            test_data = json.dumps({
                'user': {'username': 'testuser'},
                'entries': []
            }, indent=2)

            # Save to storage
            default_storage.save(storage_path, ContentFile(test_data.encode('utf-8')))
            created_paths.append(storage_path)

            return filename, storage_path

        yield _create_file

        # Cleanup: remove only files created by this fixture
        for storage_path in created_paths:
            try:
                default_storage.delete(storage_path)
            except Exception:
                pass

    def test_download_export_success(self, client, create_export_file):
        """User can download their own export with valid signed token."""
        user = UserFactory()
        client.force_login(user)

        # Create export file
        filename, storage_path = create_export_file(user.id)

        # Generate signed token
        signer = TimestampSigner(salt='export-download')
        signed_token = signer.sign(filename)

        # Request download
        response = client.get(
            reverse('api:export-download'),
            {'token': signed_token}
        )

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        assert 'attachment' in response['Content-Disposition']
        assert f'quietpage_export_{user.username}.json' in response['Content-Disposition']

    def test_download_export_missing_token(self, client):
        """Download fails when token is missing."""
        user = UserFactory()
        client.force_login(user)

        response = client.get(reverse('api:export-download'))

        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'required' in data['error'].lower()

    def test_download_export_expired_token(self, client, create_export_file):
        """Download fails when token has expired (>48 hours)."""
        user = UserFactory()
        client.force_login(user)

        # Create export file
        filename, storage_path = create_export_file(user.id)

        # Generate signed token and mock it as expired
        signer = TimestampSigner(salt='export-download')

        # Create a token with an old timestamp (more than 48 hours ago)
        with mock.patch('django.core.signing.time.time') as mock_time:
            # Set time to 49 hours ago (172800 + 3600 seconds)
            mock_time.return_value = timezone.now().timestamp() - 176400
            signed_token = signer.sign(filename)

        # Request download with expired token
        response = client.get(
            reverse('api:export-download'),
            {'token': signed_token}
        )

        assert response.status_code == 410  # HTTP 410 GONE
        data = response.json()
        assert 'error' in data
        assert 'expired' in data['error'].lower()

    def test_download_export_invalid_signature(self, client):
        """Download fails when token signature is invalid or tampered."""
        user = UserFactory()
        client.force_login(user)

        # Use a tampered/invalid token
        invalid_token = 'user_1_export_20240101_120000.json:invalid:signature'

        response = client.get(
            reverse('api:export-download'),
            {'token': invalid_token}
        )

        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'invalid' in data['error'].lower() or 'tampered' in data['error'].lower()

    def test_download_export_invalid_filename_format(self, client):
        """Download fails when filename doesn't match expected format."""
        user = UserFactory()
        client.force_login(user)

        # Create a signed token with invalid filename format
        signer = TimestampSigner(salt='export-download')
        invalid_filename = 'malicious_file.json'
        signed_token = signer.sign(invalid_filename)

        response = client.get(
            reverse('api:export-download'),
            {'token': signed_token}
        )

        assert response.status_code == 404
        data = response.json()
        assert 'error' in data

    def test_download_export_wrong_user(self, client, create_export_file):
        """User cannot download another user's export."""
        user1 = UserFactory()
        user2 = UserFactory()
        client.force_login(user2)

        # Create export file for user1
        filename, storage_path = create_export_file(user1.id)

        # Generate signed token for user1's file
        signer = TimestampSigner(salt='export-download')
        signed_token = signer.sign(filename)

        # User2 tries to download user1's export
        response = client.get(
            reverse('api:export-download'),
            {'token': signed_token}
        )

        assert response.status_code == 404  # Should not reveal file exists
        data = response.json()
        assert 'error' in data

    def test_download_export_file_not_found(self, client):
        """Download fails when export file doesn't exist in storage."""
        import uuid
        user = UserFactory()
        client.force_login(user)

        # Create token for non-existent file (valid UUID format)
        fake_uuid = uuid.uuid4()
        filename = f'user_{user.id}_{fake_uuid}.json'
        signer = TimestampSigner(salt='export-download')
        signed_token = signer.sign(filename)

        response = client.get(
            reverse('api:export-download'),
            {'token': signed_token}
        )

        assert response.status_code == 404
        data = response.json()
        assert 'error' in data

    def test_download_export_requires_auth(self, client, create_export_file):
        """Unauthenticated users cannot download exports."""
        user = UserFactory()

        # Create export file
        filename, storage_path = create_export_file(user.id)

        # Generate signed token
        signer = TimestampSigner(salt='export-download')
        signed_token = signer.sign(filename)

        # Try to download without authentication
        response = client.get(
            reverse('api:export-download'),
            {'token': signed_token}
        )

        assert response.status_code == 403

    def test_download_export_directory_traversal_prevention(self, client):
        """Download prevents directory traversal attacks."""
        user = UserFactory()
        client.force_login(user)

        # Try directory traversal in filename
        malicious_filename = f'user_{user.id}_export_../../etc/passwd.json'
        signer = TimestampSigner(salt='export-download')
        signed_token = signer.sign(malicious_filename)

        response = client.get(
            reverse('api:export-download'),
            {'token': signed_token}
        )

        # Should fail validation due to filename format regex
        assert response.status_code == 404
        data = response.json()
        assert 'error' in data

    def test_download_export_rejects_old_timestamp_format(self, client, create_export_file):
        """Old timestamp-based filenames are rejected (security fix)."""
        user = UserFactory()
        client.force_login(user)

        # Create export file with old timestamp format
        filename, storage_path = create_export_file(user.id, use_uuid=False)

        # Generate signed token
        signer = TimestampSigner(salt='export-download')
        signed_token = signer.sign(filename)

        # Should be rejected due to new UUID-only validation
        response = client.get(
            reverse('api:export-download'),
            {'token': signed_token}
        )

        assert response.status_code == 404
        data = response.json()
        assert 'error' in data

    def test_uuid_filename_is_unguessable(self, create_export_file):
        """UUID-based filenames are cryptographically random and unguessable."""
        import uuid
        import re

        # Create two export files for same user
        filename1, _ = create_export_file(user_id=1, use_uuid=True)
        filename2, _ = create_export_file(user_id=1, use_uuid=True)

        # Extract UUIDs from filenames
        pattern = r'user_\d+_([a-f0-9\-]{36})\.json'
        uuid1_str = re.search(pattern, filename1).group(1)
        uuid2_str = re.search(pattern, filename2).group(1)

        # Verify they are valid UUIDs
        uuid1 = uuid.UUID(uuid1_str)
        uuid2 = uuid.UUID(uuid2_str)

        # Verify they are different (not sequential/predictable)
        assert uuid1 != uuid2

        # Verify they are version 4 UUIDs (random)
        assert uuid1.version == 4
        assert uuid2.version == 4


@pytest.mark.integration
@pytest.mark.django_db
class TestEmailChangeVerifyView:
    """Test email change verification endpoint."""

    def test_verify_valid_token(self, client):
        """Test verifying email change with valid token."""
        from apps.accounts.models import EmailChangeRequest
        from apps.accounts.tests.factories import UserFactory
        from django.utils import timezone
        from datetime import timedelta
        from unittest.mock import patch

        user = UserFactory(email='old@example.com')
        client.force_login(user)

        # Create email change request
        request = EmailChangeRequest.objects.create(
            user=user,
            new_email='new@example.com',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        url = reverse('api:email-change-verify', kwargs={'token': str(request.pk)})

        with patch('apps.accounts.tasks.send_email_changed_notification_async.delay'):
            response = client.get(url)

        assert response.status_code == 200

        # Verify email was updated
        user.refresh_from_db()
        assert user.email == 'new@example.com'

        # Verify request was marked as verified
        request.refresh_from_db()
        assert request.is_verified is True

    def test_verify_expired_token(self, client):
        """Test verifying email change with expired token."""
        from apps.accounts.models import EmailChangeRequest
        from apps.accounts.tests.factories import UserFactory
        from django.utils import timezone
        from datetime import timedelta

        user = UserFactory(email='old@example.com')
        client.force_login(user)

        # Create expired request
        request = EmailChangeRequest.objects.create(
            user=user,
            new_email='new@example.com',
            expires_at=timezone.now() - timedelta(hours=1)
        )

        url = reverse('api:email-change-verify', kwargs={'token': str(request.pk)})
        response = client.get(url)

        assert response.status_code == 400

    def test_verify_already_verified_token(self, client):
        """Test verifying already verified email change."""
        from apps.accounts.models import EmailChangeRequest
        from apps.accounts.tests.factories import UserFactory
        from django.utils import timezone
        from datetime import timedelta

        user = UserFactory(email='old@example.com')
        client.force_login(user)

        # Create already verified request
        request = EmailChangeRequest.objects.create(
            user=user,
            new_email='new@example.com',
            expires_at=timezone.now() + timedelta(hours=24),
            is_verified=True,
            verified_at=timezone.now()
        )

        url = reverse('api:email-change-verify', kwargs={'token': str(request.pk)})
        response = client.get(url)

        assert response.status_code == 400
