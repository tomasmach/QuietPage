"""
Utility functions for QuietPage configuration.
"""

from django.core.management.utils import get_random_secret_key


def generate_secret_key():
    """
    Generate a new Django SECRET_KEY.
    
    Usage:
        from config.utils import generate_secret_key
        print(generate_secret_key())
    
    Or from command line:
        python -c "from config.utils import generate_secret_key; print(generate_secret_key())"
    
    Returns:
        str: A cryptographically secure random secret key.
    """
    return get_random_secret_key()


if __name__ == '__main__':
    # Allow running this file directly to generate a key
    print(generate_secret_key())
