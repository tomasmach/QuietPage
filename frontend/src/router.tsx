import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { PublicRoute } from './components/auth/PublicRoute';
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { DashboardPage } from './pages/DashboardPage';
import { StatsPage } from './pages/StatsPage';
import { ArchivePage } from './pages/ArchivePage';
import { EntryEditorPage } from './pages/EntryEditorPage';
import { SettingsLayout } from './components/layout/SettingsLayout';
import {
  ProfileSettingsPage,
  GoalsSettingsPage,
  PrivacySettingsPage,
  SecuritySettingsPage,
  DeleteAccountPage,
} from './pages/settings';

export const router = createBrowserRouter([
  // Public routes
  {
    path: '/',
    element: (
      <PublicRoute>
        <HomePage />
      </PublicRoute>
    ),
  },
  {
    path: '/login',
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: '/signup',
    element: (
      <PublicRoute>
        <SignupPage />
      </PublicRoute>
    ),
  },

  // Protected routes
  {
    path: '/onboarding',
    element: (
      <ProtectedRoute>
        <OnboardingPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/stats',
    element: (
      <ProtectedRoute>
        <StatsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/archive',
    element: (
      <ProtectedRoute>
        <ArchivePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/entries',
    element: (
      <ProtectedRoute>
        <ArchivePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/entries/new',
    element: (
      <ProtectedRoute>
        <EntryEditorPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/entries/:id',
    element: (
      <ProtectedRoute>
        <EntryEditorPage />
      </ProtectedRoute>
    ),
  },
  // Settings routes with nested layout
  {
    path: '/settings',
    element: (
      <ProtectedRoute>
        <SettingsLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/settings/profile" replace />,
      },
      {
        path: 'profile',
        element: <ProfileSettingsPage />,
      },
      {
        path: 'goals',
        element: <GoalsSettingsPage />,
      },
      {
        path: 'privacy',
        element: <PrivacySettingsPage />,
      },
      {
        path: 'security',
        element: <SecuritySettingsPage />,
      },
      {
        path: 'delete-account',
        element: <DeleteAccountPage />,
      },
    ],
  },

  // Catch-all redirect
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
