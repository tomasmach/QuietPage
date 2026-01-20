"""
Tests for EncryptionKey model.

Tests encryption key generation, storage, and retrieval.

Note: EncryptionKey is auto-created by signal when a User is created.
These tests verify the model functionality using the auto-created keys.
"""

import pytest
from django.db import IntegrityError
from apps.accounts.models import EncryptionKey
from apps.accounts.tests.factories import UserFactory


@pytest.mark.unit
@pytest.mark.encryption
class TestEncryptionKeyModel:
    """Test EncryptionKey model functionality."""

    def test_encryption_key_creation(self):
        """Test that encryption key is auto-created when user is created."""
        user = UserFactory()
        # Key is auto-created by signal
        key = user.encryption_key

        assert key.id is not None
        assert key.user == user
        assert key.version == 1
        assert key.is_active is True
        assert key.key is not None
        assert len(key.key) > 0

    def test_encryption_key_is_unique_per_user(self):
        """Test that each user can only have one encryption key."""
        user = UserFactory()
        # Key already exists from signal, attempting to create another should fail

        with pytest.raises(IntegrityError):
            EncryptionKey.objects.create(user=user)

    def test_get_decrypted_key_returns_valid_fernet_key(self):
        """Test that decrypted key can be used with Fernet."""
        from cryptography.fernet import Fernet

        user = UserFactory()
        # Key is auto-created by signal
        enc_key = user.encryption_key

        decrypted = enc_key.get_decrypted_key()
        # Should not raise - valid Fernet key
        fernet = Fernet(decrypted)

        # Test encryption/decryption works
        test_data = b"test message"
        encrypted = fernet.encrypt(test_data)
        decrypted_data = fernet.decrypt(encrypted)
        assert decrypted_data == test_data

    def test_key_is_stored_encrypted(self):
        """Test that the key stored in DB is not the raw Fernet key."""
        user = UserFactory()
        # Key is auto-created by signal
        enc_key = user.encryption_key

        # Raw DB value should not be a valid Fernet key directly
        raw_value = enc_key.key
        decrypted_value = enc_key.get_decrypted_key()

        # They should be different (raw is encrypted)
        assert raw_value != decrypted_value.decode() if isinstance(decrypted_value, bytes) else raw_value != decrypted_value
