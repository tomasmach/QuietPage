"""
Root conftest.py for pytest configuration.

This file provides global fixtures and configuration for all tests.
"""

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from cryptography.fernet import Fernet
import tempfile
import os


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Configure database for testing.
    
    Sets up encryption key and other test-specific settings.
    """
    with django_db_blocker.unblock():
        # Ensure encryption key is set for tests
        if not hasattr(settings, 'FIELD_ENCRYPTION_KEY'):
            settings.FIELD_ENCRYPTION_KEY = Fernet.generate_key()


@pytest.fixture
def temp_media_dir(settings):
    """
    Create temporary media directory for file upload tests.
    
    Automatically cleans up after test completion.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        settings.MEDIA_ROOT = temp_dir
        yield temp_dir


@pytest.fixture
def sample_avatar():
    """
    Create a simple test image file for avatar upload tests.
    
    Returns:
        SimpleUploadedFile: A valid JPEG image file
    """
    # Create a minimal valid JPEG (1x1 red pixel)
    jpeg_data = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c'
        b'\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c'
        b'\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00'
        b'\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00'
        b'\x08\x01\x01\x00\x00?\x00\x7f\x00\xff\xd9'
    )
    return SimpleUploadedFile(
        "test_avatar.jpg",
        jpeg_data,
        content_type="image/jpeg"
    )


@pytest.fixture
def large_avatar():
    """
    Create a test image that exceeds the 2MB size limit.
    
    Returns:
        SimpleUploadedFile: An oversized image file
    """
    # Create a minimal valid JPEG header/footer with large data in between
    jpeg_header = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c'
        b'\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c'
        b'\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00'
        b'\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00'
        b'\x08\x01\x01\x00\x00?\x00'
    )
    # Add padding to make it > 2MB, then close the JPEG
    jpeg_padding = b'\x00' * (3 * 1024 * 1024)  # 3MB of padding
    jpeg_footer = b'\xff\xd9'
    large_data = jpeg_header + jpeg_padding + jpeg_footer
    
    return SimpleUploadedFile(
        "large_avatar.jpg",
        large_data,
        content_type="image/jpeg"
    )


@pytest.fixture
def invalid_image_file():
    """
    Create an invalid image file (non-image content).
    
    Returns:
        SimpleUploadedFile: A text file pretending to be an image
    """
    return SimpleUploadedFile(
        "fake_image.jpg",
        b"This is not an image",
        content_type="text/plain"
    )


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Grant database access to all tests automatically.
    
    This fixture is marked with autouse=True, so pytest-django will
    enable database access for every test function without requiring
    the @pytest.mark.django_db decorator.
    """
    pass


@pytest.fixture
def encryption_key():
    """
    Generate a valid Fernet encryption key for testing.
    
    Returns:
        bytes: A valid Fernet encryption key
    """
    return Fernet.generate_key()


@pytest.fixture(autouse=True)
def override_static_storage(settings):
    """
    Override static files storage for tests to avoid manifest errors.
    
    Use StaticFilesStorage instead of CompressedManifestStaticFilesStorage
    to avoid "Missing staticfiles manifest entry" errors in tests.
    """
    settings.STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }


@pytest.fixture(autouse=True)
def configure_test_authentication(settings):
    """
    Configure authentication for testing.
    
    Remove allauth middleware and configure session/auth settings for tests.
    """
    # Remove problematic middleware for tests
    middleware = [
        m for m in settings.MIDDLEWARE 
        if 'allauth' not in m.lower()
    ]
    settings.MIDDLEWARE = middleware
    
    # Set authentication backends
    settings.AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
    ]
    
    # Disable session saving on every request
    settings.SESSION_SAVE_EVERY_REQUEST = False


@pytest.fixture(autouse=True)
def disable_throttling_for_tests(request, settings):
    """
    Disable rate limiting for all tests to prevent 429 errors.

    DRF throttling should not apply during tests as it causes false failures
    when multiple test requests are made rapidly.

    This fixture is skipped for tests marked with @pytest.mark.rate_limiting,
    which need actual throttle limits to test rate limiting behavior.
    """
    # Skip this fixture if the test is marked with rate_limiting marker
    if 'rate_limiting' in request.keywords:
        return

    # Set extremely high throttle rates instead of removing them
    # This prevents ImproperlyConfigured errors while effectively disabling throttling
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        'anon': '10000/hour',
        'user': '10000/hour',
        'register': '10000/hour',
        'entries_create': '10000/day',
        'avatar_upload': '10000/hour',
        'statistics': '10000/hour',
    }


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    """
    Clear Django cache before each test to prevent cache pollution.

    Tests that create data and make API calls with caching enabled can leave
    cached responses that affect subsequent tests, causing false failures.
    This fixture ensures each test starts with a clean cache.
    """
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()
