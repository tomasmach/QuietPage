"""
Comprehensive pytest tests for settings API views.

Tests all settings API endpoints in apps/api/settings_views.py with 80%+ coverage.
"""

import json
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.tests.factories import UserFactory
from apps.journal.tests.factories import EntryFactory

User = get_user_model()


@pytest.mark.views
@pytest.mark.unit
class TestDeleteAccountAPIView:
    """Test DeleteAccountView for account deletion."""

    def test_delete_account_success_with_SMAZAT(self, client):
        """User can delete account with correct password and 'SMAZAT' confirmation."""
        user = UserFactory()
        client.force_login(user)

        response = client.post(
            reverse('api:settings-delete-account'),
            data=json.dumps({'password': 'testpass123', 'confirmation_text': 'SMAZAT'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'uspesne smazan' in data['message'].lower()

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
        user = UserFactory(first_name='Jan', last_name='Novak', bio='Test bio')
        client.force_login(user)

        response = client.get(reverse('api:settings-profile'))

        assert response.status_code == 200
        data = response.json()
        assert data['first_name'] == 'Jan'
        assert data['last_name'] == 'Novak'
        assert data['bio'] == 'Test bio'

    def test_patch_profile_update(self, client):
        """User can update their profile settings."""
        user = UserFactory(first_name='Old', last_name='Name')
        client.force_login(user)

        response = client.patch(
            reverse('api:settings-profile'),
            data=json.dumps({'first_name': 'New', 'last_name': 'Name'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == 'New'
        assert user.last_name == 'Name'

    def test_patch_profile_update_partial(self, client):
        """User can update partial profile fields."""
        user = UserFactory(first_name='Jan', last_name='Novak')
        client.force_login(user)

        response = client.patch(
            reverse('api:settings-profile'),
            data=json.dumps({'bio': 'New bio'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == 'Jan'
        assert user.last_name == 'Novak'
        assert user.bio == 'New bio'

    def test_profile_requires_auth(self, client):
        """Unauthenticated users cannot access profile settings."""
        response = client.get(reverse('api:settings-profile'))
        assert response.status_code == 403

        response = client.patch(
            reverse('api:settings-profile'),
            data=json.dumps({'first_name': 'Test'}),
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
        user = UserFactory()
        client.force_login(user)

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
class TestChangeEmailAPIView:
    """Test ChangeEmailView for email change."""

    def test_change_email_success(self, client):
        """User can change email successfully."""
        user = UserFactory(email='old@example.com')
        client.force_login(user)

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
        user.refresh_from_db()
        assert user.email == 'new@example.com'

    def test_change_email_already_taken(self, client):
        """Cannot change email to one already taken by another user."""
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

    def test_change_email_same_as_current(self, client):
        """Cannot change email to the same email."""
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
