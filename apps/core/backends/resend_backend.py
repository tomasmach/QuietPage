"""
Custom Django email backend using Resend.

This backend integrates Resend's email API with Django's email system.
"""

import logging
import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """
    Email backend that sends emails using Resend API.

    Configuration:
        - RESEND_API_KEY: Your Resend API key (required)
        - DEFAULT_FROM_EMAIL: Default sender email address
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        resend.api_key = settings.RESEND_API_KEY

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number sent.

        Args:
            email_messages: List of Django EmailMessage objects

        Returns:
            int: Number of emails sent successfully
        """
        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send_message(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email via Resend: {e}", exc_info=True)
                if not self.fail_silently:
                    raise

        return num_sent

    def _send_message(self, message):
        """
        Send a single EmailMessage via Resend API.

        Args:
            message: Django EmailMessage object

        Returns:
            bool: True if email was sent successfully
        """
        if not message.recipients():
            return False

        # Prepare email parameters for Resend
        params = {
            'from': message.from_email or settings.DEFAULT_FROM_EMAIL,
            'to': message.recipients(),
            'subject': message.subject,
        }

        # Add plain text body
        if message.body:
            params['text'] = message.body

        # Send via Resend API
        response = resend.Emails.send(params)

        logger.info(
            f"Email sent via Resend: {message.subject} "
            f"to {len(message.recipients())} recipient(s) "
            f"(id: {response.get('id', 'unknown')})"
        )

        return True
