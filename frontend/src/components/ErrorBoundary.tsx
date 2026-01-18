import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

// Safe fallback component that doesn't rely on context hooks
function ErrorFallback({
  error,
  onReset
}: {
  error: Error | null;
  onReset: () => void;
}) {
  // Get language from localStorage for safe fallback, with try-catch for SSR/testing
  let language = 'cs';
  try {
    language = localStorage?.getItem('quietpage-language') || 'cs';
  } catch {
    // Fallback to Czech if localStorage is not available
  }

  const messages = {
    cs: {
      title: 'Něco se pokazilo',
      message: 'Aplikace narazila na neočekávanou chybu. Zkuste stránku obnovit.',
      details: 'Technické detaily',
      tryAgain: 'Zkusit znovu',
      goHome: 'Zpět na úvod',
    },
    en: {
      title: 'Something went wrong',
      message: 'The application encountered an unexpected error. Try refreshing the page.',
      details: 'Technical details',
      tryAgain: 'Try again',
      goHome: 'Go to home',
    },
  };

  const t = messages[language as keyof typeof messages] || messages.cs;

  return (
    <div className="min-h-screen bg-app flex items-center justify-center p-4">
      <div className="bg-panel border border-border p-8 max-w-lg w-full shadow-hard">
        <h1 className="text-2xl font-bold text-error mb-4">
          {t.title}
        </h1>
        <p className="text-muted mb-4">
          {t.message}
        </p>
        {import.meta.env.DEV && error && (
          <details className="mb-4">
            <summary className="cursor-pointer text-muted hover:text-main">
              {t.details}
            </summary>
            <pre className="mt-2 p-4 bg-app border border-border text-sm overflow-auto max-h-48">
              {error.message}
              {'\n\n'}
              {error.stack}
            </pre>
          </details>
        )}
        <div className="flex gap-4">
          <button
            onClick={onReset}
            className="px-4 py-2 bg-accent text-white border border-border hover:opacity-90 transition-opacity"
          >
            {t.tryAgain}
          </button>
          <button
            onClick={() => window.location.href = '/'}
            className="px-4 py-2 bg-panel border border-border hover:bg-app transition-colors"
          >
            {t.goHome}
          </button>
        </div>
      </div>
    </div>
  );
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });

    // Log error to console in development
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // TODO: Send to error tracking service (Sentry) in production
    // if (import.meta.env.PROD) {
    //   Sentry.captureException(error, { extra: { errorInfo } });
    // }
  }

  handleReset = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return <ErrorFallback error={this.state.error} onReset={this.handleReset} />;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
