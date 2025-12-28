"""
Security logging utilities for QuietPage.

This module provides utilities for logging security-related events
such as password changes, email changes, account deletions, etc.
"""

import logging

# Dedicated logger for security events
security_logger = logging.getLogger('security')


def log_security_event(event_type, user, request=None, details=None):
    """
    Log security-related events with contextual information.

    Args:
        event_type: Type of security event (e.g., 'PASSWORD_CHANGE', 'EMAIL_CHANGE')
        user: User instance (or None for anonymous events)
        request: HTTP request object (optional, for IP logging)
        details: Additional details dict (optional)

    Example:
        log_security_event('PASSWORD_CHANGE', request.user, request)
        log_security_event('ACCOUNT_DELETION', user, request, {'reason': 'user_requested'})
    """
    extra = {
        'event_type': event_type,
        'user_id': user.id if user else None,
        'username': user.username if user else None,
        'ip': get_client_ip(request) if request else None,
        'details': details or {},
    }

    security_logger.info(f"Security: {event_type}", extra=extra)


def get_client_ip(request):
    """
    Extract client IP address from request.

    Handles X-Forwarded-For header (for proxies/load balancers)
    and falls back to REMOTE_ADDR.

    Args:
        request: HTTP request object

    Returns:
        str: Client IP address
    """
    if not request:
        return None

    # Check X-Forwarded-For header (for proxies)
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        # X-Forwarded-For can contain multiple IPs, take the first (client IP)
        return x_forwarded.split(',')[0].strip()

    # Fallback to REMOTE_ADDR
    return request.META.get('REMOTE_ADDR')
