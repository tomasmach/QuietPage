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
