# Google OAuth Integration Design

## Overview

Add Google OAuth login to QuietPage with automatic account linking based on email.

## Requirements

- Google OAuth button on login and signup pages only
- Automatic account linking: if user with matching email exists, link Google account automatically
- Backend redirect flow (not frontend token flow)
- Respect existing session-based authentication

## Technical Approach

Using `django-allauth` (already installed v65.13.1) with backend redirect flow.

## Backend Changes

### 1. Settings Configuration (`config/settings/base.py`)

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    # ... existing middleware ...
    'allauth.account.middleware.AccountMiddleware',  # after AuthenticationMiddleware
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Google email is already verified

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True  # key for account linking
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True  # automatic linking

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomSocialAccountAdapter'
```

### 2. URL Routing (`config/urls.py`)

```python
urlpatterns = [
    # ... existing urls ...
    path('api/v1/auth/social/', include('allauth.socialaccount.urls')),
]
```

### 3. Custom Adapter (`apps/accounts/adapters.py`)

```python
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from apps.accounts.models import User

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        """Redirect to frontend after successful OAuth."""
        user = request.user
        if not user.onboarding_completed:
            return settings.FRONTEND_URL + '/onboarding'
        return settings.FRONTEND_URL + '/dashboard'

    def authentication_error(self, request, provider_id, error, exception, extra_context):
        """Redirect to frontend with error on OAuth failure."""
        from django.shortcuts import redirect
        return redirect(settings.FRONTEND_URL + '/login?error=oauth_failed')

    def populate_user(self, request, sociallogin, data):
        """Generate username for new OAuth users."""
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            base = data.get('email', '').split('@')[0]
            user.username = self._generate_unique_username(base)
        return user

    def _generate_unique_username(self, base):
        """Generate unique username from email prefix."""
        import re
        # Clean base: only alphanumeric, underscore, dot
        base = re.sub(r'[^a-zA-Z0-9_.]', '', base)[:20]
        if not base:
            base = 'user'

        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        return username
```

### 4. Environment Variables

Add to `.env`:
```
GOOGLE_CLIENT_ID=<from Google Cloud Console>
GOOGLE_CLIENT_SECRET=<from Google Cloud Console>
FRONTEND_URL=http://localhost:5173
```

Add to `config/settings/base.py`:
```python
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:5173')
```

### 5. Database Migration

Run after configuration:
```bash
uv run python manage.py migrate
```

This creates allauth tables: `socialaccount_socialaccount`, `socialaccount_socialapp`, `socialaccount_socialtoken`.

### 6. Google OAuth App Setup (Django Admin)

After migration, configure via Django admin or fixture:
- Provider: Google
- Client ID: from Google Cloud Console
- Secret: from Google Cloud Console
- Sites: add current site

## Frontend Changes

### 1. Google Login Button (`frontend/src/components/auth/GoogleLoginButton.tsx`)

```tsx
import { useLanguage } from '@/contexts/LanguageContext';

export function GoogleLoginButton() {
  const { t } = useLanguage();

  const handleGoogleLogin = () => {
    window.location.href = '/api/v1/auth/social/google/login/';
  };

  return (
    <button
      type="button"
      onClick={handleGoogleLogin}
      className="w-full flex items-center justify-center gap-3 px-4 py-3
                 border border-border bg-bg-panel text-text-main
                 shadow-hard hover:translate-x-[2px] hover:translate-y-[2px]
                 hover:shadow-none transition-all font-mono"
    >
      <GoogleIcon />
      <span>{t('auth.continueWithGoogle')}</span>
    </button>
  );
}

function GoogleIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24">
      <path
        fill="currentColor"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="currentColor"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="currentColor"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="currentColor"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  );
}
```

### 2. OAuth Divider Component (`frontend/src/components/auth/OAuthDivider.tsx`)

```tsx
import { useLanguage } from '@/contexts/LanguageContext';

export function OAuthDivider() {
  const { t } = useLanguage();

  return (
    <div className="flex items-center gap-4 my-6">
      <div className="flex-1 h-px bg-border" />
      <span className="text-text-muted text-sm font-mono">{t('auth.or')}</span>
      <div className="flex-1 h-px bg-border" />
    </div>
  );
}
```

### 3. Update LoginPage (`frontend/src/pages/LoginPage.tsx`)

Add at top of form:
```tsx
import { GoogleLoginButton } from '@/components/auth/GoogleLoginButton';
import { OAuthDivider } from '@/components/auth/OAuthDivider';

// Inside component, handle OAuth errors from URL
const [searchParams] = useSearchParams();
const oauthError = searchParams.get('error');

useEffect(() => {
  if (oauthError === 'oauth_cancelled') {
    toast.error(t('auth.oauthCancelled'));
  } else if (oauthError === 'oauth_failed') {
    toast.error(t('auth.oauthFailed'));
  }
}, [oauthError]);

// In JSX, before the form:
<GoogleLoginButton />
<OAuthDivider />
{/* existing form */}
```

### 4. Update SignupPage (`frontend/src/pages/SignupPage.tsx`)

Same pattern as LoginPage - add GoogleLoginButton and OAuthDivider before the form.

### 5. Translation Keys

Add to language files:
```json
{
  "auth": {
    "continueWithGoogle": "Continue with Google",
    "or": "or",
    "oauthCancelled": "Google login was cancelled",
    "oauthFailed": "Google login failed. Please try again."
  }
}
```

## OAuth Flow

```
1. User clicks "Continue with Google" button
2. Browser redirects to /api/v1/auth/social/google/login/
3. django-allauth redirects to Google OAuth consent screen
4. User authenticates with Google
5. Google redirects to /api/v1/auth/social/google/login/callback/
6. django-allauth:
   - Validates OAuth token
   - Finds existing user by email OR creates new user
   - Links Google account to user
   - Creates Django session
7. CustomSocialAccountAdapter redirects to frontend:
   - /onboarding (new user)
   - /dashboard (existing user)
8. Frontend AuthContext detects session via /auth/me/ endpoint
```

## Account Linking Behavior

| Scenario | Behavior |
|----------|----------|
| New user (email doesn't exist) | Create account, set `onboarding_completed=False`, redirect to `/onboarding` |
| Existing user (email matches) | Link Google account, login, redirect to `/dashboard` |
| User cancels OAuth consent | Redirect to `/login?error=oauth_cancelled` |
| Google API error | Redirect to `/login?error=oauth_failed` |

## Google Cloud Console Setup

1. Go to https://console.cloud.google.com/
2. Create or select project
3. Enable Google+ API
4. Go to Credentials → Create OAuth 2.0 Client ID
5. Application type: Web application
6. Authorized redirect URIs:
   - Development: `http://localhost:8000/api/v1/auth/social/google/login/callback/`
   - Production: `https://yourdomain.com/api/v1/auth/social/google/login/callback/`
7. Copy Client ID and Client Secret to `.env`

## Security Considerations

- OAuth tokens are handled server-side only (never exposed to frontend)
- Session-based auth maintained (HTTP-only cookies)
- CSRF protection still active for all endpoints
- Account linking only happens when Google email is verified
- No sensitive data stored from Google (only email for linking)

## Testing Plan

1. **New user flow**: OAuth with new email → creates account → redirects to onboarding
2. **Existing user flow**: OAuth with existing email → links account → redirects to dashboard
3. **Cancel flow**: Cancel at Google consent → redirects to login with error
4. **Error handling**: Invalid callback → redirects to login with error
5. **Session persistence**: After OAuth login, refresh page → stays logged in
