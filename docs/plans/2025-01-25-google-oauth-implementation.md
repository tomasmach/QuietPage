# Google OAuth Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Google OAuth login with automatic account linking based on email.

**Architecture:** Backend redirect flow using django-allauth (already installed). User clicks Google button → redirect to Django OAuth endpoint → Google consent → callback to Django → session created → redirect to frontend.

**Tech Stack:** django-allauth 65.13.1, React 19, TypeScript, Tailwind CSS

---

## Task 1: Configure django-allauth in settings

**Files:**
- Modify: `config/settings/base.py:31-50` (INSTALLED_APPS)
- Modify: `config/settings/base.py:52-64` (MIDDLEWARE)
- Modify: `config/settings/base.py:212-215` (AUTHENTICATION_BACKENDS)

**Step 1: Add allauth to INSTALLED_APPS**

In `config/settings/base.py`, find `INSTALLED_APPS` and add after `'axes'`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth

    # Third-party
    'rest_framework',
    'corsheaders',
    'taggit',
    'axes',  # Brute force protection
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Local apps
    'apps.accounts',
    'apps.journal',
    'apps.api',
    'apps.core',  # Infrastructure tasks
]
```

**Step 2: Add SITE_ID setting**

After `INSTALLED_APPS`, add:

```python
# Django Sites Framework (required by allauth)
SITE_ID = 1
```

**Step 3: Add AccountMiddleware to MIDDLEWARE**

In `MIDDLEWARE`, add after `'axes.middleware.AxesMiddleware'`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # After AuthenticationMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**Step 4: Add allauth authentication backend**

Update `AUTHENTICATION_BACKENDS`:

```python
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # MUST be first for rate limiting
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

**Step 5: Commit**

```bash
git add config/settings/base.py
git commit -m "feat: add django-allauth to installed apps and middleware"
```

---

## Task 2: Add allauth configuration settings

**Files:**
- Modify: `config/settings/base.py` (add at end of file)
- Modify: `.env.example` (add Google OAuth vars)

**Step 1: Add allauth settings to base.py**

At the end of `config/settings/base.py`, add:

```python
# ============================================
# GOOGLE OAUTH CONFIGURATION (django-allauth)
# ============================================

# Frontend URL for OAuth redirects
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Allauth base settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Google email already verified

# Social account settings
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True  # Enable account linking by email
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True  # Auto-connect on email match

# Custom adapter for redirect handling
SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomSocialAccountAdapter'

# Google OAuth provider settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
        },
    }
}
```

**Step 2: Add OAuth variables to .env.example**

After the `SITE_URL` line in `.env.example`, add:

```bash
# ============================================================================
# GOOGLE OAUTH SETTINGS
# ============================================================================

# Frontend URL for OAuth redirects (same as SITE_URL for development)
FRONTEND_URL=http://localhost:5173

# Google OAuth credentials (from Google Cloud Console)
# 1. Go to https://console.cloud.google.com/
# 2. Create or select project
# 3. Enable Google+ API
# 4. Go to Credentials → Create OAuth 2.0 Client ID
# 5. Application type: Web application
# 6. Authorized redirect URIs:
#    - Dev: http://localhost:8000/api/v1/auth/social/google/login/callback/
#    - Prod: https://yourdomain.com/api/v1/auth/social/google/login/callback/
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Step 3: Commit**

```bash
git add config/settings/base.py .env.example
git commit -m "feat: add django-allauth configuration for Google OAuth"
```

---

## Task 3: Create custom social account adapter

**Files:**
- Create: `apps/accounts/adapters.py`

**Step 1: Create adapter file**

Create `apps/accounts/adapters.py`:

```python
"""
Custom adapters for django-allauth social authentication.

Handles OAuth redirect logic and username generation for new OAuth users.
"""

import re
from django.conf import settings
from django.shortcuts import redirect
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account authentication.

    Handles:
    - Redirect URLs after successful OAuth login
    - Error redirects to frontend
    - Username generation for new OAuth users
    """

    def get_login_redirect_url(self, request):
        """Redirect to frontend after successful OAuth login."""
        user = request.user
        if not user.onboarding_completed:
            return f"{settings.FRONTEND_URL}/onboarding"
        return f"{settings.FRONTEND_URL}/dashboard"

    def authentication_error(
        self, request, provider_id, error=None, exception=None, extra_context=None
    ):
        """Redirect to frontend with error on OAuth failure."""
        return redirect(f"{settings.FRONTEND_URL}/login?error=oauth_failed")

    def populate_user(self, request, sociallogin, data):
        """Generate username for new OAuth users from email."""
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            email = data.get('email', '')
            base = email.split('@')[0] if email else 'user'
            user.username = self._generate_unique_username(base)
        return user

    def _generate_unique_username(self, base: str) -> str:
        """
        Generate a unique username from email prefix.

        Args:
            base: The email prefix to use as username base

        Returns:
            A unique username that doesn't exist in the database
        """
        from apps.accounts.models import User

        # Clean base: only alphanumeric, underscore, dot (max 20 chars)
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

**Step 2: Verify the file works**

```bash
uv run python -c "from apps.accounts.adapters import CustomSocialAccountAdapter; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add apps/accounts/adapters.py
git commit -m "feat: add custom social account adapter for OAuth redirects"
```

---

## Task 4: Add OAuth URL routes

**Files:**
- Modify: `config/urls.py:34-47`

**Step 1: Add allauth URLs**

In `config/urls.py`, add the allauth social URLs. Update the urlpatterns:

```python
urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    # Health check endpoint (unauthenticated, for monitoring)
    path('api/health/', HealthCheckView.as_view(), name='health-check'),
    # API v1 routes
    path('api/v1/', include('apps.api.urls', namespace='api')),
    # OAuth routes (django-allauth)
    path('api/v1/auth/social/', include('allauth.socialaccount.urls')),
    # SEO files - must be served from root URL for search engines
    path('sitemap.xml', views.SitemapView.as_view(), name='sitemap'),
    path('robots.txt', views.RobotsView.as_view(), name='robots'),
    # Catch-all pattern for React SPA - MUST be last
    re_path(rf'^(?!api/|{admin_pattern.rstrip("/")}(?:/|$)|__debug__/).*$', views.SPAView.as_view(), name='spa'),
]
```

**Step 2: Commit**

```bash
git add config/urls.py
git commit -m "feat: add OAuth URL routes for django-allauth"
```

---

## Task 5: Run database migrations

**Step 1: Create migrations for allauth tables**

```bash
uv run python manage.py migrate
```

Expected: Migrations for `sites`, `socialaccount` tables applied.

**Step 2: Create site entry**

```bash
uv run python manage.py shell -c "
from django.contrib.sites.models import Site
site, created = Site.objects.update_or_create(
    id=1,
    defaults={'domain': 'localhost:8000', 'name': 'QuietPage Development'}
)
print(f'Site {'created' if created else 'updated'}: {site.domain}')
"
```

**Step 3: Commit**

No commit needed (migrations are auto-generated, site is dev data).

---

## Task 6: Create GoogleLoginButton component

**Files:**
- Create: `frontend/src/components/auth/GoogleLoginButton.tsx`

**Step 1: Create the component**

Create `frontend/src/components/auth/GoogleLoginButton.tsx`:

```tsx
import { useLanguage } from '@/contexts/LanguageContext';

/**
 * Google OAuth login button.
 * Redirects to backend OAuth endpoint which handles the full OAuth flow.
 */
export function GoogleLoginButton() {
  const { t } = useLanguage();

  const handleGoogleLogin = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = '/api/v1/auth/social/google/login/';
  };

  return (
    <button
      type="button"
      onClick={handleGoogleLogin}
      className="w-full flex items-center justify-center gap-3 px-4 py-3
                 border-2 border-border bg-bg-panel text-text-main
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
    <svg className="w-5 h-5" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/auth/GoogleLoginButton.tsx
git commit -m "feat: add GoogleLoginButton component"
```

---

## Task 7: Create OAuthDivider component

**Files:**
- Create: `frontend/src/components/auth/OAuthDivider.tsx`

**Step 1: Create the component**

Create `frontend/src/components/auth/OAuthDivider.tsx`:

```tsx
import { useLanguage } from '@/contexts/LanguageContext';

/**
 * Visual divider between OAuth buttons and traditional login form.
 */
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

**Step 2: Commit**

```bash
git add frontend/src/components/auth/OAuthDivider.tsx
git commit -m "feat: add OAuthDivider component"
```

---

## Task 8: Add translation keys

**Files:**
- Modify: `frontend/src/locales/cs.ts:27-46` (interface) and `frontend/src/locales/cs.ts:578-597` (values)
- Modify: `frontend/src/locales/en.ts` (same sections)

**Step 1: Update TypeScript interface in cs.ts**

Find the `auth` interface section (around line 27) and add new keys:

```typescript
  auth: {
    login: string;
    logout: string;
    register: string;
    signup: string;
    username: string;
    usernameOrEmail: string;
    email: string;
    password: string;
    passwordConfirm: string;
    forgotPassword: string;
    noAccount: string;
    hasAccount: string;
    createAccount: string;
    backToHome: string;
    loggingIn: string;
    signingUp: string;
    loginError: string;
    signupError: string;
    // OAuth
    continueWithGoogle: string;
    or: string;
    oauthCancelled: string;
    oauthFailed: string;
  };
```

**Step 2: Update Czech translations in cs.ts**

Find the Czech `auth` values section (around line 578) and add:

```typescript
  auth: {
    login: 'Přihlásit se',
    logout: 'Odhlásit se',
    register: 'Registrace',
    signup: 'Registrovat se',
    username: 'Uživatelské jméno',
    usernameOrEmail: 'Uživatelské jméno nebo e-mail',
    email: 'E-mail',
    password: 'Heslo',
    passwordConfirm: 'Heslo znovu',
    forgotPassword: 'Zapomenuté heslo?',
    noAccount: 'Nemáš účet?',
    hasAccount: 'Máš účet?',
    createAccount: 'Vytvořit účet',
    backToHome: 'Zpět',
    loggingIn: 'Přihlašuji...',
    signingUp: 'Registruji...',
    loginError: 'Nesprávné přihlašovací údaje',
    signupError: 'Registrace se nezdařila',
    // OAuth
    continueWithGoogle: 'Pokračovat přes Google',
    or: 'nebo',
    oauthCancelled: 'Přihlášení přes Google bylo zrušeno',
    oauthFailed: 'Přihlášení přes Google selhalo. Zkuste to znovu.',
  },
```

**Step 3: Update English translations in en.ts**

Same pattern for en.ts - add the OAuth keys to both interface and values:

```typescript
    // OAuth (in values section)
    continueWithGoogle: 'Continue with Google',
    or: 'or',
    oauthCancelled: 'Google login was cancelled',
    oauthFailed: 'Google login failed. Please try again.',
```

**Step 4: Commit**

```bash
git add frontend/src/locales/cs.ts frontend/src/locales/en.ts
git commit -m "feat: add OAuth translation keys"
```

---

## Task 9: Update LoginPage with OAuth

**Files:**
- Modify: `frontend/src/pages/LoginPage.tsx`

**Step 1: Add imports**

At the top of `LoginPage.tsx`, add to existing imports:

```tsx
import { useState, useEffect, type FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
```

And add new component imports:

```tsx
import { GoogleLoginButton } from '@/components/auth/GoogleLoginButton';
import { OAuthDivider } from '@/components/auth/OAuthDivider';
```

**Step 2: Add OAuth error handling**

Inside `LoginPage` function, after the existing state declarations, add:

```tsx
  const [searchParams] = useSearchParams();

  // Handle OAuth errors from URL query params
  useEffect(() => {
    const error = searchParams.get('error');
    if (error === 'oauth_cancelled') {
      toast.error(t('auth.oauthCancelled'));
    } else if (error === 'oauth_failed') {
      toast.error(t('auth.oauthFailed'));
    }
  }, [searchParams, toast, t]);
```

**Step 3: Add OAuth components to JSX**

Inside the form card `<div className="bg-bg-panel border-2 border-border shadow-hard p-8">`, before the `<form>` tag, add:

```tsx
          {/* Google OAuth */}
          <GoogleLoginButton />
          <OAuthDivider />

          <form onSubmit={handleSubmit} className="space-y-6">
```

**Step 4: Verify the build**

```bash
cd frontend && npm run build
```

Expected: Build succeeds without errors.

**Step 5: Commit**

```bash
git add frontend/src/pages/LoginPage.tsx
git commit -m "feat: add Google OAuth button to LoginPage"
```

---

## Task 10: Update SignupPage with OAuth

**Files:**
- Modify: `frontend/src/pages/SignupPage.tsx`

**Step 1: Add imports**

Add to existing imports in `SignupPage.tsx`:

```tsx
import { useSearchParams } from 'react-router-dom';
import { GoogleLoginButton } from '@/components/auth/GoogleLoginButton';
import { OAuthDivider } from '@/components/auth/OAuthDivider';
```

Update the existing import to include `useEffect`:

```tsx
import { useState, useEffect, type FormEvent } from 'react';
```

**Step 2: Add OAuth error handling**

Inside `SignupPage` function, after existing state declarations, add:

```tsx
  const [searchParams] = useSearchParams();

  // Handle OAuth errors from URL query params
  useEffect(() => {
    const error = searchParams.get('error');
    if (error === 'oauth_cancelled') {
      toast.error(t('auth.oauthCancelled'));
    } else if (error === 'oauth_failed') {
      toast.error(t('auth.oauthFailed'));
    }
  }, [searchParams, toast, t]);
```

**Step 3: Add OAuth components to JSX**

Inside the form card, before the `<form>` tag, add:

```tsx
          {/* Google OAuth */}
          <GoogleLoginButton />
          <OAuthDivider />

          <form onSubmit={handleSubmit} className="space-y-6">
```

**Step 4: Verify the build**

```bash
cd frontend && npm run build
```

Expected: Build succeeds without errors.

**Step 5: Commit**

```bash
git add frontend/src/pages/SignupPage.tsx
git commit -m "feat: add Google OAuth button to SignupPage"
```

---

## Task 11: Add component exports

**Files:**
- Modify: `frontend/src/components/auth/index.ts` (if exists) or create barrel export

**Step 1: Check if index.ts exists and update**

If `frontend/src/components/auth/index.ts` exists, add:

```tsx
export { GoogleLoginButton } from './GoogleLoginButton';
export { OAuthDivider } from './OAuthDivider';
```

If it doesn't exist, the direct imports from Tasks 9-10 are sufficient.

**Step 2: Commit (if changes made)**

```bash
git add frontend/src/components/auth/index.ts
git commit -m "feat: export OAuth components from auth barrel"
```

---

## Task 12: Write adapter tests

**Files:**
- Create: `apps/accounts/tests/test_adapters.py`

**Step 1: Create test file**

Create `apps/accounts/tests/test_adapters.py`:

```python
"""Tests for custom social account adapter."""

import pytest
from unittest.mock import Mock, patch
from django.test import RequestFactory
from apps.accounts.adapters import CustomSocialAccountAdapter
from apps.accounts.models import User


@pytest.mark.django_db
class TestCustomSocialAccountAdapter:
    """Tests for CustomSocialAccountAdapter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = CustomSocialAccountAdapter()
        self.factory = RequestFactory()

    def test_get_login_redirect_url_onboarding_not_completed(self):
        """User who hasn't completed onboarding goes to /onboarding."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            onboarding_completed=False,
        )
        request = self.factory.get('/')
        request.user = user

        url = self.adapter.get_login_redirect_url(request)

        assert '/onboarding' in url

    def test_get_login_redirect_url_onboarding_completed(self):
        """User who completed onboarding goes to /dashboard."""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            onboarding_completed=True,
        )
        request = self.factory.get('/')
        request.user = user

        url = self.adapter.get_login_redirect_url(request)

        assert '/dashboard' in url

    def test_generate_unique_username_simple(self):
        """Generate username from clean email prefix."""
        username = self.adapter._generate_unique_username('john')
        assert username == 'john'

    def test_generate_unique_username_with_special_chars(self):
        """Special characters are removed from username."""
        username = self.adapter._generate_unique_username('john+test@')
        assert username == 'johntest'

    def test_generate_unique_username_collision(self):
        """Numeric suffix added when username exists."""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123',
        )

        username = self.adapter._generate_unique_username('existinguser')

        assert username == 'existinguser1'

    def test_generate_unique_username_multiple_collisions(self):
        """Multiple numeric suffixes handled correctly."""
        User.objects.create_user(
            username='popular',
            email='popular@example.com',
            password='testpass123',
        )
        User.objects.create_user(
            username='popular1',
            email='popular1@example.com',
            password='testpass123',
        )

        username = self.adapter._generate_unique_username('popular')

        assert username == 'popular2'

    def test_generate_unique_username_empty_base(self):
        """Empty base defaults to 'user'."""
        username = self.adapter._generate_unique_username('')
        assert username == 'user'

    def test_generate_unique_username_truncates_long_base(self):
        """Long usernames are truncated to 20 chars."""
        long_name = 'a' * 50
        username = self.adapter._generate_unique_username(long_name)
        assert len(username) <= 20
```

**Step 2: Run tests**

```bash
uv run pytest apps/accounts/tests/test_adapters.py -v
```

Expected: All tests pass.

**Step 3: Commit**

```bash
git add apps/accounts/tests/test_adapters.py
git commit -m "test: add adapter tests for OAuth username generation"
```

---

## Task 13: Write frontend component tests

**Files:**
- Create: `frontend/src/components/auth/__tests__/GoogleLoginButton.test.tsx`

**Step 1: Create test file**

Create `frontend/src/components/auth/__tests__/GoogleLoginButton.test.tsx`:

```tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { GoogleLoginButton } from '../GoogleLoginButton';

// Mock useLanguage
vi.mock('@/contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'auth.continueWithGoogle': 'Continue with Google',
      };
      return translations[key] || key;
    },
  }),
}));

describe('GoogleLoginButton', () => {
  beforeEach(() => {
    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: { href: '' },
      writable: true,
    });
  });

  it('renders button with correct text', () => {
    render(<GoogleLoginButton />);

    expect(screen.getByRole('button')).toHaveTextContent('Continue with Google');
  });

  it('renders Google icon', () => {
    render(<GoogleLoginButton />);

    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('redirects to OAuth endpoint on click', () => {
    render(<GoogleLoginButton />);

    fireEvent.click(screen.getByRole('button'));

    expect(window.location.href).toBe('/api/v1/auth/social/google/login/');
  });
});
```

**Step 2: Run tests**

```bash
cd frontend && npm run test:run -- --filter GoogleLoginButton
```

Expected: All tests pass.

**Step 3: Commit**

```bash
git add frontend/src/components/auth/__tests__/GoogleLoginButton.test.tsx
git commit -m "test: add GoogleLoginButton component tests"
```

---

## Task 14: Manual integration test

**Prerequisites:**
- Google OAuth credentials configured in `.env`
- Backend running: `make run`
- Frontend running: `cd frontend && npm run dev`

**Step 1: Test new user OAuth flow**

1. Open http://localhost:5173/login
2. Click "Pokračovat přes Google"
3. Complete Google OAuth consent
4. Verify redirect to /onboarding (new user)

**Step 2: Test existing user OAuth flow**

1. Create user with same email as Google account (if not exists)
2. Logout
3. Click "Pokračovat přes Google" on login page
4. Verify redirect to /dashboard
5. Verify same user account (check username in settings)

**Step 3: Test OAuth cancellation**

1. Click "Pokračovat přes Google"
2. Cancel at Google consent screen
3. Verify redirect to /login?error=oauth_cancelled
4. Verify error toast appears

---

## Summary

After completing all tasks:

1. **Backend changes:**
   - django-allauth configured in settings
   - Custom adapter for redirects and username generation
   - OAuth URLs mounted at `/api/v1/auth/social/`

2. **Frontend changes:**
   - GoogleLoginButton component
   - OAuthDivider component
   - Updated LoginPage and SignupPage
   - Translation keys for OAuth

3. **Tests:**
   - Adapter unit tests
   - Component tests

4. **Manual testing:**
   - New user flow → onboarding
   - Existing user flow → dashboard (account linking)
   - Error handling for cancelled/failed OAuth
