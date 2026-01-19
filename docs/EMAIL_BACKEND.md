# Email Backend Documentation

## Overview

QuietPage uses Resend as the email service provider for all transactional emails. Emails are sent asynchronously via Celery tasks to avoid blocking HTTP requests.

## Email Types

### 1. Welcome Email
- **Trigger:** User registration
- **Template:** `templates/accounts/emails/welcome.txt`
- **Task:** `send_welcome_email_async`
- **Recipient:** New user's email

### 2. Password Reset Request
- **Trigger:** User clicks "Forgot password?"
- **Template:** `templates/accounts/emails/password_reset_request.txt`
- **Task:** `send_password_reset_email_async`
- **Token:** 1-hour expiration, single-use
- **Recipient:** User's email

### 3. Password Changed Notification
- **Trigger:** User changes password
- **Template:** `templates/accounts/emails/password_changed.txt`
- **Task:** `send_password_changed_email_async`
- **Recipient:** User's email

### 4. Email Change Verification
- **Trigger:** User requests email change
- **Template:** `templates/accounts/emails/email_verification.txt`
- **Task:** `send_email_change_verification_async`
- **Token:** 24-hour expiration
- **Recipient:** New email address

### 5. Email Changed Notification
- **Trigger:** Email change verified
- **Template:** `templates/accounts/emails/email_changed_notification.txt`
- **Task:** `send_email_changed_notification_async`
- **Recipient:** Old email address (security notification)

### 6. Account Deleted Confirmation
- **Trigger:** User deletes account
- **Template:** `templates/accounts/emails/account_deleted.txt`
- **Task:** `send_account_deleted_email_async`
- **Recipient:** User's email

## Configuration

### Environment Variables

```bash
# Required for production
RESEND_API_KEY=re_your_api_key_here
DEFAULT_FROM_EMAIL=info@quietpage.app
```

### Development

Development uses Django's console backend to print emails to terminal:

```python
# config/settings/development.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production

Production uses Resend backend:

```python
# config/settings/base.py
EMAIL_BACKEND = 'apps.core.backends.resend_backend.ResendEmailBackend'
```

## Testing Emails

### Manual Testing (Development)

1. Start development server: `make dev`
2. Register a new user
3. Check terminal output for welcome email content

### Automated Testing

```bash
# Test email backend
uv run pytest apps/core/tests/test_resend_backend.py -v

# Test email tasks
uv run pytest apps/accounts/tests/test_email_tasks.py -v

# Test email integration
uv run pytest apps/api/tests/test_password_reset_views.py -v
```

## Rate Limiting

Password reset and email change are rate limited to prevent abuse:

- Password reset: 5 requests per hour per IP
- Email change: 3 requests per hour per user

## Security

- All reset/verification tokens are cryptographically signed
- Tokens have short expiration windows (1 hour for password, 24 hours for email)
- Tokens are single-use only
- Email enumeration is prevented (always returns success)
- All security events are logged

## Troubleshooting

### Emails not sending in production

1. Check Resend API key is set: `echo $RESEND_API_KEY`
2. Check Celery is running: `celery -A config inspect active`
3. Check logs: `tail -f logs/django.log | grep email`
4. Verify domain in Resend dashboard

### Task retry failures

Emails are retried 3 times with exponential backoff (60s, 120s, 240s). Check Celery logs for failure details.

## API Endpoints

### Password Reset

```bash
# Request reset
POST /api/v1/auth/password-reset/request/
{
  "email": "user@example.com"
}

# Confirm reset
POST /api/v1/auth/password-reset/confirm/
{
  "token": "...",
  "new_password": "...",
  "new_password_confirm": "..."
}
```

### Email Change

```bash
# Request change
POST /api/v1/settings/security/email/
{
  "new_email": "new@example.com",
  "password": "current_password"
}

# Verify change
GET /api/v1/auth/email-change/verify/<token>/
```
