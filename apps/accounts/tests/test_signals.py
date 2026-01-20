"""
Comprehensive tests for accounts app signal handlers.

Tests all signal handlers in apps/accounts/signals.py including:
- delete_old_avatar_on_update: cleanup when avatar changes
- delete_avatar_on_user_delete: cleanup on user deletion
- create_encryption_key_for_user: auto-create EncryptionKey on user creation
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import User, EncryptionKey
from apps.accounts.tests.factories import UserFactory


@pytest.mark.signals
@pytest.mark.unit
class TestDeleteOldAvatarOnUpdate:
    """Tests for delete_old_avatar_on_update signal handler."""

    def test_deletes_old_avatar_when_new_avatar_uploaded(self, sample_avatar, temp_media_dir):
        """Test that old avatar is deleted when user uploads new one."""
        user = UserFactory()
        
        # Upload first avatar
        old_avatar = SimpleUploadedFile(
            "old_avatar.jpg",
            sample_avatar.read(),
            content_type="image/jpeg"
        )
        user.avatar = old_avatar
        user.save()
        
        old_avatar_name = user.avatar.name
        
        # Upload new avatar
        sample_avatar.seek(0)
        new_avatar = SimpleUploadedFile(
            "new_avatar.jpg",
            sample_avatar.read(),
            content_type="image/jpeg"
        )
        
        # Create a mock for the old avatar's delete method
        mock_old_avatar = MagicMock()
        mock_old_avatar.name = old_avatar_name
        mock_old_avatar.__bool__.return_value = True
        
        # Patch User.objects.get to return a user with the mocked avatar
        with patch.object(User.objects, 'get') as mock_get:
            mock_old_user = MagicMock()
            mock_old_user.avatar = mock_old_avatar
            mock_get.return_value = mock_old_user
            
            user.avatar = new_avatar
            user.save()
            
            # Old avatar delete should have been called
            mock_old_avatar.delete.assert_called_once_with(save=False)

    def test_does_not_delete_when_avatar_unchanged(self, sample_avatar, temp_media_dir):
        """Test that avatar is not deleted when it hasn't changed."""
        user = UserFactory()

        # Upload avatar
        user.avatar = sample_avatar
        user.save()

        # Update other field without changing avatar
        with patch.object(user.avatar, 'delete') as mock_delete:
            user.bio = 'Updated bio'
            user.save()

            # Delete should not be called
            mock_delete.assert_not_called()

    def test_does_not_error_on_new_user_creation(self):
        """Test that signal doesn't error when creating new user with avatar."""
        # Create user with avatar in one go
        user = UserFactory.build()
        
        # This should not raise an error
        user.save()
        
        assert user.pk is not None

    def test_handles_avatar_set_to_none(self, sample_avatar, temp_media_dir):
        """Test handling when avatar is set to None (removed)."""
        user = UserFactory()
        
        # Upload avatar
        user.avatar = sample_avatar
        user.save()
        
        old_avatar_name = user.avatar.name
        
        # Create a mock for the old avatar's delete method
        mock_old_avatar = MagicMock()
        mock_old_avatar.name = old_avatar_name
        mock_old_avatar.__bool__.return_value = True
        
        # Remove avatar
        with patch.object(User.objects, 'get') as mock_get:
            mock_old_user = MagicMock()
            mock_old_user.avatar = mock_old_avatar
            mock_get.return_value = mock_old_user
            
            user.avatar = None
            user.save()
            
            # Old avatar should be deleted
            mock_old_avatar.delete.assert_called_once_with(save=False)

    def test_handles_user_does_not_exist_gracefully(self):
        """Test that signal handles case where old user doesn't exist."""
        # Create a user instance without saving
        user = User(username='testuser', email='test@example.com')
        user.pk = 99999  # Set a fake PK that doesn't exist in DB
        
        # This should not raise an error
        user.save()
        
        # Cleanup
        user.delete()

    def test_handles_delete_failure_gracefully(self, sample_avatar, temp_media_dir):
        """Test that signal handles file deletion failures gracefully."""
        user = UserFactory()
        
        # Upload first avatar
        sample_avatar.seek(0)
        old_avatar = SimpleUploadedFile(
            "old.jpg",
            sample_avatar.read(),
            content_type="image/jpeg"
        )
        user.avatar = old_avatar
        user.save()
        
        # Mock delete to raise exception
        sample_avatar.seek(0)
        new_avatar = SimpleUploadedFile(
            "new.jpg",
            sample_avatar.read(),
            content_type="image/jpeg"
        )
        
        with patch.object(user.avatar, 'delete', side_effect=Exception('Delete failed')):
            # Should not raise exception - error is caught
            user.avatar = new_avatar
            user.save()
            
            # User should still be saved with new avatar
            user.refresh_from_db()
            assert user.avatar is not None

    @patch('apps.accounts.signals.logger')
    def test_logs_warning_on_delete_failure(self, mock_logger, sample_avatar, temp_media_dir):
        """Test that failures are logged as warnings."""
        user = UserFactory()
        
        # Upload avatar
        sample_avatar.seek(0)
        user.avatar = SimpleUploadedFile(
            "old.jpg",
            sample_avatar.read(),
            content_type="image/jpeg"
        )
        user.save()
        
        old_avatar_name = user.avatar.name
        
        # Mock delete to fail
        sample_avatar.seek(0)
        new_avatar = SimpleUploadedFile(
            "new.jpg",
            sample_avatar.read(),
            content_type="image/jpeg"
        )
        
        # Create a mock for the old avatar's delete method that raises an exception
        mock_old_avatar = MagicMock()
        mock_old_avatar.name = old_avatar_name
        mock_old_avatar.__bool__.return_value = True
        mock_old_avatar.delete.side_effect = Exception('Storage error')
        
        with patch.object(User.objects, 'get') as mock_get:
            mock_old_user = MagicMock()
            mock_old_user.avatar = mock_old_avatar
            mock_get.return_value = mock_old_user
            
            user.avatar = new_avatar
            user.save()
            
            # Logger warning should be called
            mock_logger.warning.assert_called_once()
            warning_message = mock_logger.warning.call_args[0][0]
            assert 'Failed to delete old avatar' in warning_message


@pytest.mark.signals
@pytest.mark.unit
class TestDeleteAvatarOnUserDelete:
    """Tests for delete_avatar_on_user_delete signal handler."""

    def test_deletes_avatar_when_user_deleted(self, sample_avatar, temp_media_dir):
        """Test that avatar is deleted when user account is deleted."""
        user = UserFactory()
        
        # Upload avatar
        user.avatar = sample_avatar
        user.save()
        
        # Mock the delete method
        with patch.object(user.avatar, 'delete') as mock_delete:
            user.delete()
            
            # Avatar delete should have been called
            mock_delete.assert_called_once_with(save=False)

    def test_does_not_error_when_user_has_no_avatar(self):
        """Test that signal doesn't error when user has no avatar."""
        user = UserFactory()
        user.avatar = None
        user.save()
        
        # Should not raise an error
        user.delete()

    def test_handles_delete_failure_gracefully(self, sample_avatar, temp_media_dir):
        """Test that file deletion failures don't prevent user deletion."""
        user = UserFactory()
        
        # Upload avatar
        user.avatar = sample_avatar
        user.save()
        
        # Mock delete to raise exception
        with patch.object(user.avatar, 'delete', side_effect=Exception('Storage error')):
            # Should not raise exception
            user.delete()
            
            # User should be deleted
            assert not User.objects.filter(pk=user.pk).exists()

    @patch('apps.accounts.signals.logger')
    def test_logs_warning_on_delete_failure(self, mock_logger, sample_avatar, temp_media_dir):
        """Test that failures are logged as warnings."""
        user = UserFactory()
        
        # Upload avatar
        user.avatar = sample_avatar
        user.save()
        user_pk = user.pk
        
        # Mock delete to fail
        with patch.object(user.avatar, 'delete', side_effect=Exception('Disk error')):
            user.delete()
            
            # Logger warning should be called
            mock_logger.warning.assert_called_once()
            warning_message = mock_logger.warning.call_args[0][0]
            assert 'Failed to delete avatar' in warning_message
            assert str(user_pk) in warning_message

    def test_avatar_deleted_before_user(self, sample_avatar, temp_media_dir):
        """Test that signal fires before user is actually deleted (pre_delete)."""
        user = UserFactory()
        user.avatar = sample_avatar
        user.save()
        
        delete_called = []
        
        # Patch delete to track when it's called
        original_delete = user.avatar.delete
        
        def track_delete(*args, **kwargs):
            # At this point, user should still exist in DB
            delete_called.append(User.objects.filter(pk=user.pk).exists())
            return original_delete(*args, **kwargs)
        
        with patch.object(user.avatar, 'delete', side_effect=track_delete):
            user.delete()
            
            # Delete should have been called while user still existed
            assert len(delete_called) == 1
            assert delete_called[0] is True

    def test_multiple_users_deleted_each_avatar_removed(self, sample_avatar, temp_media_dir):
        """Test that each user's avatar is properly deleted in bulk operations."""
        # Create multiple users with avatars
        users = []
        for i in range(3):
            user = UserFactory()
            sample_avatar.seek(0)
            user.avatar = SimpleUploadedFile(
                f"avatar{i}.jpg",
                sample_avatar.read(),
                content_type="image/jpeg"
            )
            user.save()
            users.append(user)
        
        delete_count = 0
        
        def count_deletes(*args, **kwargs):
            nonlocal delete_count
            delete_count += 1
        
        # Delete all users
        with patch('apps.accounts.models.User.avatar.field.storage.delete', side_effect=count_deletes):
            for user in users:
                # Mock at instance level
                with patch.object(user.avatar, 'delete', side_effect=count_deletes):
                    user.delete()
        
        # Each avatar delete should have been attempted
        assert delete_count == 3

    def test_avatar_deleted_via_mock_verification(self, sample_avatar, temp_media_dir):
        """Test that avatar delete is called with correct parameters via mock."""
        user = UserFactory()
        user.avatar = sample_avatar
        user.save()
        
        avatar_name = user.avatar.name
        
        # Create a mock for the avatar's delete method
        mock_avatar = MagicMock()
        mock_avatar.name = avatar_name
        mock_avatar.__bool__.return_value = True
        
        # Patch the avatar on the instance being deleted
        with patch.object(user, 'avatar', mock_avatar):
            user.delete()

            # Avatar should have been deleted
            mock_avatar.delete.assert_called_once_with(save=False)


@pytest.mark.unit
@pytest.mark.encryption
class TestEncryptionKeySignal:
    """Test automatic EncryptionKey creation on user creation."""

    def test_encryption_key_created_on_user_creation(self):
        """Test that EncryptionKey is auto-created when user is created."""
        user = UserFactory()

        assert hasattr(user, 'encryption_key')
        assert user.encryption_key is not None
        assert isinstance(user.encryption_key, EncryptionKey)

    def test_encryption_key_not_duplicated_on_user_save(self):
        """Test that saving user doesn't create duplicate keys."""
        user = UserFactory()
        original_key_id = user.encryption_key.id

        user.bio = "Updated bio"
        user.save()
        user.refresh_from_db()

        assert user.encryption_key.id == original_key_id
        assert EncryptionKey.objects.filter(user=user).count() == 1
