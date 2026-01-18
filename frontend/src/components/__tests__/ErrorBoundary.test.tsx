import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { useState } from 'react';
import { ErrorBoundary } from '../ErrorBoundary';

// Component that throws an error when shouldThrow is true
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
}

describe('ErrorBoundary', () => {
  // Mock localStorage
  const localStorageMock = (() => {
    let store: Record<string, string> = {};

    return {
      getItem: (key: string) => store[key] || null,
      setItem: (key: string, value: string) => {
        store[key] = value.toString();
      },
      removeItem: (key: string) => {
        delete store[key];
      },
      clear: () => {
        store = {};
      },
    };
  })();

  beforeEach(() => {
    // Suppress console.error for these tests
    vi.spyOn(console, 'error').mockImplementation(() => {});

    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    });

    // Clear localStorage before each test
    localStorageMock.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('renders error fallback when child component throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    // Check for Czech error message (default language)
    expect(screen.getByText('Něco se pokazilo')).toBeInTheDocument();
    expect(screen.getByText(/Aplikace narazila na neočekávanou chybu/)).toBeInTheDocument();
  });

  it('shows try again and go home buttons', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByRole('button', { name: /Zkusit znovu/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Zpět na úvod/i })).toBeInTheDocument();
  });

  it('renders custom fallback when provided', () => {
    const customFallback = <div>Custom error message</div>;

    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom error message')).toBeInTheDocument();
  });

  it('resets error state when try again is clicked', () => {
    // Track if child should throw an error
    function TestComponent() {
      const [shouldThrow, setShouldThrow] = useState(true);
      const [key, setKey] = useState(0);

      // When the user fixes the error source and resets the boundary
      const handleFix = () => {
        setShouldThrow(false);
        setKey(k => k + 1);  // Change key to reset ErrorBoundary
      };

      return (
        <div>
          <button onClick={handleFix} data-testid="fix-button">
            Fix error
          </button>
          <ErrorBoundary key={key}>
            <ThrowError shouldThrow={shouldThrow} />
          </ErrorBoundary>
        </div>
      );
    }

    render(<TestComponent />);

    // Verify error is shown
    expect(screen.getByText('Něco se pokazilo')).toBeInTheDocument();

    // Get the try again button in the error boundary
    const tryAgainButton = screen.getByRole('button', { name: /Zkusit znovu/i });
    expect(tryAgainButton).toBeInTheDocument();

    // Click try again - this resets the ErrorBoundary's internal state
    fireEvent.click(tryAgainButton);

    // The error is shown again because the child still throws
    // (this is expected behavior - the error boundary reset its state but child still has the issue)
    expect(screen.getByText('Něco se pokazilo')).toBeInTheDocument();

    // Now fix the actual error by clicking fix button (changes shouldThrow AND resets ErrorBoundary with new key)
    const fixButton = screen.getByTestId('fix-button');
    fireEvent.click(fixButton);

    // Now the ErrorBoundary should successfully show the working component
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('uses English messages when language is set to en', () => {
    // Set language to English
    localStorage.setItem('quietpage-language', 'en');

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText(/The application encountered an unexpected error/)).toBeInTheDocument();

    // Clean up
    localStorage.removeItem('quietpage-language');
  });
});
