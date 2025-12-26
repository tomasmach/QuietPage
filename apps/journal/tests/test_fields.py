"""
Comprehensive tests for journal.fields.

Tests the EncryptedTextField custom field including:
- Encryption/decryption round-trip
- Empty values handling
- Invalid encryption key handling
- Corrupted data handling
- get_fernet_key() configuration
- Unicode and special character support
"""

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet, InvalidToken
from apps.journal.fields import (
    EncryptedTextField,
    DecryptionError,
    get_fernet_key,
)
from apps.journal.models import Entry
from apps.accounts.tests.factories import UserFactory


@pytest.mark.unit
@pytest.mark.encryption
class TestGetFernetKey:
    """Test get_fernet_key() function."""
    
    def test_get_fernet_key_returns_bytes(self):
        """Test that get_fernet_key returns bytes."""
        key = get_fernet_key()
        
        assert isinstance(key, bytes)
    
    def test_get_fernet_key_with_string_setting(self, settings):
        """Test get_fernet_key with string key in settings."""
        test_key = Fernet.generate_key()
        settings.FIELD_ENCRYPTION_KEY = test_key.decode('utf-8')
        
        key = get_fernet_key()
        
        assert isinstance(key, bytes)
        assert key == test_key
    
    def test_get_fernet_key_with_bytes_setting(self, settings):
        """Test get_fernet_key with bytes key in settings."""
        test_key = Fernet.generate_key()
        settings.FIELD_ENCRYPTION_KEY = test_key
        
        key = get_fernet_key()
        
        assert isinstance(key, bytes)
        assert key == test_key
    
    def test_get_fernet_key_missing_raises_error(self, settings):
        """Test that missing key raises ImproperlyConfigured."""
        # Remove the key
        if hasattr(settings, 'FIELD_ENCRYPTION_KEY'):
            delattr(settings, 'FIELD_ENCRYPTION_KEY')
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            get_fernet_key()
        
        assert 'FIELD_ENCRYPTION_KEY must be set' in str(exc_info.value)
    
    def test_get_fernet_key_none_raises_error(self, settings):
        """Test that None key raises ImproperlyConfigured."""
        settings.FIELD_ENCRYPTION_KEY = None
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            get_fernet_key()
        
        assert 'FIELD_ENCRYPTION_KEY must be set' in str(exc_info.value)
    
    def test_get_fernet_key_empty_string_raises_error(self, settings):
        """Test that empty string key raises ImproperlyConfigured."""
        settings.FIELD_ENCRYPTION_KEY = ''
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            get_fernet_key()
        
        assert 'FIELD_ENCRYPTION_KEY must be set' in str(exc_info.value)
    
    def test_get_fernet_key_invalid_format_raises_error(self, settings):
        """Test that invalid key format raises ImproperlyConfigured."""
        settings.FIELD_ENCRYPTION_KEY = 'invalid-key-format'
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            get_fernet_key()
        
        assert 'FIELD_ENCRYPTION_KEY is invalid' in str(exc_info.value)
    
    def test_get_fernet_key_wrong_length_raises_error(self, settings):
        """Test that wrong length key raises ImproperlyConfigured."""
        settings.FIELD_ENCRYPTION_KEY = 'short'
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            get_fernet_key()
        
        assert 'FIELD_ENCRYPTION_KEY is invalid' in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.encryption
class TestEncryptedTextField:
    """Test EncryptedTextField basic functionality."""
    
    def test_field_initialization(self):
        """Test that field can be initialized."""
        field = EncryptedTextField()
        
        assert field.description == "An encrypted text field"
    
    def test_field_removes_max_length(self):
        """Test that max_length is removed from kwargs."""
        # Should not raise even if max_length is provided
        field = EncryptedTextField(max_length=100)
        
        # max_length should be removed
        assert not hasattr(field, 'max_length') or field.max_length is None
    
    def test_field_deconstruct(self):
        """Test field deconstruct for migrations."""
        field = EncryptedTextField(help_text="Test field")
        _name, _path, _args, kwargs = field.deconstruct()
        
        assert 'max_length' not in kwargs
        assert kwargs.get('help_text') == "Test field"


@pytest.mark.unit
@pytest.mark.encryption
class TestEncryptionDecryption:
    """Test encryption and decryption round-trip."""
    
    def test_simple_text_round_trip(self):
        """Test encrypting and decrypting simple text."""
        user = UserFactory()
        original_text = "This is a simple test."
        
        entry = Entry.objects.create(user=user, content=original_text)
        entry.refresh_from_db()
        
        assert entry.content == original_text
    
    def test_empty_string_handling(self):
        """Test that empty string is not encrypted."""
        user = UserFactory()
        
        # Create with valid content first, then update to empty
        entry = Entry.objects.create(user=user, content="Initial")
        entry.content = ""
        entry.save()
        entry.refresh_from_db()
        
        assert entry.content == ""
    
    def test_none_value_handling(self):
        """Test that None value passes through."""
        field = EncryptedTextField()
        
        # get_prep_value should return None for None input
        result = field.get_prep_value(None)
        assert result is None
        
        # from_db_value should return None for None input
        result = field.from_db_value(None, None, None)
        assert result is None
    
    def test_unicode_text_round_trip(self):
        """Test encrypting and decrypting Unicode text."""
        user = UserFactory()
        czech_text = "Příliš žluťoučký kůň úpěl ďábelské ódy. 🇨🇿"
        
        entry = Entry.objects.create(user=user, content=czech_text)
        entry.refresh_from_db()
        
        assert entry.content == czech_text
    
    def test_special_characters_round_trip(self):
        """Test encrypting and decrypting special characters."""
        user = UserFactory()
        special_text = "Special: @#$%^&*(){}[]|\\:;\"'<>,.?/~`"
        
        entry = Entry.objects.create(user=user, content=special_text)
        entry.refresh_from_db()
        
        assert entry.content == special_text
    
    def test_multiline_text_round_trip(self):
        """Test encrypting and decrypting multiline text."""
        user = UserFactory()
        multiline_text = """Line 1
Line 2
Line 3

Line 5 with blank line before"""
        
        entry = Entry.objects.create(user=user, content=multiline_text)
        entry.refresh_from_db()
        
        assert entry.content == multiline_text
    
    def test_emojis_round_trip(self):
        """Test encrypting and decrypting emojis."""
        user = UserFactory()
        emoji_text = "Happy 😊 Sad 😢 Love ❤️ Star ⭐ Fire 🔥"
        
        entry = Entry.objects.create(user=user, content=emoji_text)
        entry.refresh_from_db()
        
        assert entry.content == emoji_text
    
    def test_long_text_round_trip(self):
        """Test encrypting and decrypting long text."""
        user = UserFactory()
        long_text = "A" * 10000  # 10k characters
        
        entry = Entry.objects.create(user=user, content=long_text)
        entry.refresh_from_db()
        
        assert entry.content == long_text
        assert len(entry.content) == 10000
    
    def test_non_string_value_converted_to_string(self):
        """Test that non-string values are converted to string."""
        field = EncryptedTextField()
        
        # Test with integer
        encrypted = field.get_prep_value(123)
        assert encrypted is not None
        
        # The value should be encrypted as "123"
        f = field.get_fernet()
        decrypted = f.decrypt(encrypted.encode('utf-8')).decode('utf-8')
        assert decrypted == "123"


@pytest.mark.unit
@pytest.mark.encryption
class TestEncryptionErrors:
    """Test encryption error handling."""
    
    def test_invalid_token_raises_decryption_error(self, settings):
        """Test that invalid encrypted data raises DecryptionError."""
        user = UserFactory()
        
        # Create entry with one key
        original_key = Fernet.generate_key()
        settings.FIELD_ENCRYPTION_KEY = original_key
        entry = Entry.objects.create(user=user, content="Secret data")
        entry_id = entry.id
        
        # Change encryption key
        new_key = Fernet.generate_key()
        settings.FIELD_ENCRYPTION_KEY = new_key
        
        # Try to read entry with different key
        with pytest.raises(DecryptionError) as exc_info:
            entry = Entry.objects.get(id=entry_id)
            _ = entry.content  # Access content to trigger decryption
        
        assert 'Failed to decrypt' in str(exc_info.value)
        
        # Restore original key
        settings.FIELD_ENCRYPTION_KEY = original_key
    
    def test_corrupted_data_raises_decryption_error(self):
        """Test that corrupted encrypted data raises DecryptionError."""
        field = EncryptedTextField()
        field.name = 'test_field'
        
        # Simulate corrupted encrypted data
        corrupted_data = "corrupted-encrypted-data-12345"
        
        with pytest.raises(DecryptionError) as exc_info:
            field.from_db_value(corrupted_data, None, None)
        
        assert 'Failed to decrypt' in str(exc_info.value)
    
    def test_decryption_error_message_includes_field_name(self):
        """Test that DecryptionError includes field name."""
        field = EncryptedTextField()
        field.name = 'my_secret_field'
        
        corrupted_data = "corrupted-data"
        
        with pytest.raises(DecryptionError) as exc_info:
            field.from_db_value(corrupted_data, None, None)
        
        assert 'my_secret_field' in str(exc_info.value)
    
    def test_decryption_error_is_raised_from_invalid_token(self):
        """Test that DecryptionError is chained from InvalidToken."""
        field = EncryptedTextField()
        field.name = 'test_field'
        
        corrupted_data = "corrupted-data"
        
        with pytest.raises(DecryptionError) as exc_info:
            field.from_db_value(corrupted_data, None, None)
        
        # Check that the cause is InvalidToken
        assert isinstance(exc_info.value.__cause__, InvalidToken)


@pytest.mark.unit
@pytest.mark.encryption
class TestEncryptionSecurity:
    """Test encryption security properties."""
    
    def test_encryption_is_non_deterministic(self):
        """Test that encrypting the same value twice produces different output."""
        field = EncryptedTextField()
        
        value = "Same text"
        encrypted1 = field.get_prep_value(value)
        encrypted2 = field.get_prep_value(value)
        
        # Fernet encryption is non-deterministic (includes timestamp + random IV)
        assert encrypted1 != encrypted2
    
    def test_encrypted_data_is_base64_encoded(self):
        """Test that encrypted data is base64-encoded string."""
        field = EncryptedTextField()
        
        encrypted = field.get_prep_value("Test data")
        
        assert isinstance(encrypted, str)
        # Fernet tokens start with 'gAAAAA' (base64 of version + timestamp)
        assert encrypted.startswith('gAAAAA')
    
    def test_encrypted_data_length_is_larger(self):
        """Test that encrypted data is larger than original."""
        field = EncryptedTextField()
        
        original = "Short"
        encrypted = field.get_prep_value(original)
        
        # Encrypted data includes: version (1) + timestamp (8) + IV (16) + 
        # ciphertext (padded) + HMAC (32) = much larger
        assert len(encrypted) > len(original)
    
    def test_decryption_requires_correct_key(self, settings):
        """Test that decryption requires the correct key."""
        # Encrypt with key 1
        key1 = Fernet.generate_key()
        settings.FIELD_ENCRYPTION_KEY = key1
        
        field1 = EncryptedTextField()
        encrypted = field1.get_prep_value("Secret data")
        
        # Try to decrypt with key 2
        key2 = Fernet.generate_key()
        settings.FIELD_ENCRYPTION_KEY = key2
        
        field2 = EncryptedTextField()
        field2.name = 'test_field'
        
        with pytest.raises(DecryptionError):
            field2.from_db_value(encrypted, None, None)
        
        # Restore key1
        settings.FIELD_ENCRYPTION_KEY = key1


@pytest.mark.unit
@pytest.mark.encryption
class TestUnicodeSupport:
    """Test Unicode character support in encryption."""
    
    def test_czech_characters(self):
        """Test Czech characters."""
        user = UserFactory()
        text = "Žluťoučký kůň úpěl ďábelské ódy"
        
        entry = Entry.objects.create(user=user, content=text)
        entry.refresh_from_db()
        
        assert entry.content == text
    
    def test_mixed_czech_and_english(self):
        """Test mixed Czech and English text."""
        user = UserFactory()
        text = "Today jsem měl great den! 🎉"
        
        entry = Entry.objects.create(user=user, content=text)
        entry.refresh_from_db()
        
        assert entry.content == text
    
    def test_various_emojis(self):
        """Test various emojis."""
        user = UserFactory()
        text = "😀😃😄😁😆😅🤣😂🙂🙃😉😊😇"
        
        entry = Entry.objects.create(user=user, content=text)
        entry.refresh_from_db()
        
        assert entry.content == text
    
    def test_emoji_with_skin_tone(self):
        """Test emojis with skin tone modifiers."""
        user = UserFactory()
        text = "👋👋🏻👋🏼👋🏽👋🏾👋🏿"
        
        entry = Entry.objects.create(user=user, content=text)
        entry.refresh_from_db()
        
        assert entry.content == text
    
    def test_combined_diacritics(self):
        """Test combined diacritical marks."""
        user = UserFactory()
        text = "Café naïve résumé"
        
        entry = Entry.objects.create(user=user, content=text)
        entry.refresh_from_db()
        
        assert entry.content == text
    
    def test_cyrillic_characters(self):
        """Test Cyrillic characters."""
        user = UserFactory()
        text = "Привет мир"
        
        entry = Entry.objects.create(user=user, content=text)
        entry.refresh_from_db()
        
        assert entry.content == text
    
    def test_chinese_characters(self):
        """Test Chinese characters."""
        user = UserFactory()
        text = "你好世界"
        
        entry = Entry.objects.create(user=user, content=text)
        entry.refresh_from_db()
        
        assert entry.content == text
    
    def test_mixed_unicode_scripts(self):
        """Test mixed Unicode scripts."""
        user = UserFactory()
        text = "Hello Привет 你好 مرحبا שלום Γειά σου"
        
        entry = Entry.objects.create(user=user, content=text)
        entry.refresh_from_db()
        
        assert entry.content == text
