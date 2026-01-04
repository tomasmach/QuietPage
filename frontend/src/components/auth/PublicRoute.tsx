import { Navigate } from 'react-router-dom';
import type { ReactNode } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface PublicRouteProps {
  children: ReactNode;
}

export function PublicRoute({ children }: PublicRouteProps) {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-app">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-text-main border-t-transparent"></div>
          <p className="mt-4 text-text-main">Loading...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    // Redirect new users to onboarding, existing users to dashboard
    const redirectTo = user?.onboarding_completed ? '/dashboard' : '/onboarding';
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
}
