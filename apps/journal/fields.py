"""
Custom encrypted field implementation for Django.

Uses cryptography library (Fernet symmetric encryption) directly,
avoiding unmaintained third-party packages.

Advantages:
- Modern: Uses cryptography 46.0.3 (actively maintained)
- Simple: ~100 lines of code, easy to understand and modify
- Secure: Fernet provides authenticated encryption (AES-128-CBC + HMAC-SHA256)
- Django 6.0 compatible: No deprecated APIs
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet, InvalidToken
import base64
import logging

# Get logger for this module
logger = logging.getLogger(__name__)


class DecryptionError(Exception):
    """
    Raised when field decryption fails.
    
    This exception indicates that encrypted data could not be decrypted,
    which may be caused by:
    - Incorrect encryption key
    - Corrupted data in database
    - Data tampering
    """
    pass


def get_fernet_key():
    """
    Get Fernet encryption key from settings.
    
    Raises:
        ImproperlyConfigured: If FIELD_ENCRYPTION_KEY is not set or invalid.
    
    Returns:
        bytes: Fernet encryption key
    """
    key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    
    if not key:
        raise ImproperlyConfigured(
            'FIELD_ENCRYPTION_KEY must be set in settings. '
            'Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    
    # Ensure key is bytes
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    # Validate key format
    try:
        Fernet(key)
    except Exception as e:
        raise ImproperlyConfigured(
            f'FIELD_ENCRYPTION_KEY is invalid: {e}. '
            'It must be a 32 url-safe base64-encoded bytes.'
        )
    
    return key


class EncryptedTextField(models.TextField):
    """
    A TextField that automatically encrypts data before saving to database
    and decrypts when retrieving.
    
    Uses Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256).
    
    Usage:
        class MyModel(models.Model):
            secret_data = EncryptedTextField()
    
    Note:
        - Cannot filter or order by this field (encryption is non-deterministic)
        - Content is stored as base64-encoded encrypted bytes
        - Increases storage size by ~50-100 bytes
    """
    
    description = "An encrypted text field"
    
    def __init__(self, *args, **kwargs):
        # Remove max_length if provided (encrypted data length varies)
        kwargs.pop('max_length', None)
        super().__init__(*args, **kwargs)
    
    def get_fernet(self):
        """Get Fernet cipher instance."""
        return Fernet(get_fernet_key())
    
    def from_db_value(self, value, expression, connection):
        """
        Convert database value to Python value (decrypt).
        
        Called when data is loaded from the database.
        
        Raises:
            DecryptionError: If decryption fails for any reason.
        """
        if value is None:
            return value
        
        try:
            f = self.get_fernet()
            # Value is stored as string in DB, convert to bytes for decryption
            decrypted = f.decrypt(value.encode('utf-8'))
            return decrypted.decode('utf-8')
        except InvalidToken as e:
            # Log the failure with safe identifiers (never log raw encrypted value)
            logger.error(
                "Decryption failed for field '%s' (InvalidToken). "
                "This may indicate incorrect encryption key or data tampering. "
                "Exception: %s",
                self.name or 'unknown_field',
                str(e),
                exc_info=True,
                extra={
                    'field_name': self.name,
                    'error_type': 'InvalidToken',
                }
            )
            raise DecryptionError(
                f"Failed to decrypt field '{self.name or 'unknown_field'}': {str(e)}"
            ) from e
        except Exception as e:
            # Log any other unexpected errors
            logger.error(
                "Unexpected error during decryption of field '%s': %s",
                self.name or 'unknown_field',
                str(e),
                exc_info=True,
                extra={
                    'field_name': self.name,
                    'error_type': type(e).__name__,
                }
            )
            raise DecryptionError(
                f"Unexpected error decrypting field '{self.name or 'unknown_field'}': {str(e)}"
            ) from e
    
    def get_prep_value(self, value):
        """
        Convert Python value to database value (encrypt).
        
        Called before saving to the database.
        """
        if value is None or value == '':
            return value
        
        # Ensure value is string
        if not isinstance(value, str):
            value = str(value)
        
        f = self.get_fernet()
        # Encrypt and return as string for DB storage
        encrypted = f.encrypt(value.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    def deconstruct(self):
        """
        Support for migrations.
        
        Returns name, path, args, kwargs for recreating the field.
        """
        name, path, args, kwargs = super().deconstruct()
        # Remove max_length from kwargs if present
        kwargs.pop('max_length', None)
        return name, path, args, kwargs
