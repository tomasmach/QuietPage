import { useState, useCallback } from 'react';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

// Types for settings data
export interface ProfileSettings {
  first_name: string;
  last_name: string;
  bio: string;
  avatar?: string;
}

export interface GoalsSettings {
  daily_word_goal: number;
  timezone: string;
  preferred_writing_time: 'morning' | 'afternoon' | 'evening';
  reminder_enabled: boolean;
  reminder_time: string;
}

export interface PrivacySettings {
  email_notifications: boolean;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}

export interface ChangeEmailData {
  new_email: string;
  password: string;
}

export interface DeleteAccountData {
  password: string;
  confirmation_text: string;
}

interface UseSettingsReturn {
  // Loading and error states
  isLoading: boolean;
  error: string | null;
  success: string | null;

  // Clear messages
  clearMessages: () => void;

  // Profile
  updateProfile: (data: ProfileSettings) => Promise<boolean>;
  uploadAvatar: (file: File) => Promise<string | null>;

  // Goals
  updateGoals: (data: GoalsSettings) => Promise<boolean>;

  // Privacy
  updatePrivacy: (data: PrivacySettings) => Promise<boolean>;

  // Security
  changePassword: (data: ChangePasswordData) => Promise<boolean>;
  changeEmail: (data: ChangeEmailData) => Promise<boolean>;

  // Account deletion
  deleteAccount: (data: DeleteAccountData) => Promise<boolean>;
}

/**
 * Hook for managing user settings
 * Provides methods to update profile, goals, privacy, security settings
 */
export function useSettings(): UseSettingsReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { checkAuth, logout } = useAuth();

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  const handleRequest = useCallback(async <T>(
    requestFn: () => Promise<T>,
    successMessage?: string
  ): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await requestFn();
      if (successMessage) {
        setSuccess(successMessage);
      }
      return true;
    } catch (err) {
      // Zobraz generickou zprávu, ne surový error
      setError('Nastala chyba při ukládání nastavení. Zkuste to prosím znovu.');
      if (import.meta.env.DEV) {
        console.error('Settings error:', err);
      }
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Update profile settings (first_name, last_name, bio)
   */
  const updateProfile = useCallback(async (data: ProfileSettings): Promise<boolean> => {
    const result = await handleRequest(
      () => api.patch('/settings/profile/', data),
      'Profile updated successfully'
    );
    if (result) {
      await checkAuth(); // Refresh user data
    }
    return result;
  }, [handleRequest, checkAuth]);

  /**
   * Upload avatar image
   * Returns the URL of the uploaded avatar or null on failure
   */
  const uploadAvatar = useCallback(async (file: File): Promise<string | null> => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('avatar', file);

      // Use api client for CSRF token handling
      // We need to use fetch directly for FormData, but get CSRF token from api client
      const getCsrfToken = (): string | null => {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (const cookie of cookies) {
          const trimmed = cookie.trim();
          if (trimmed.startsWith(name + '=')) {
            return trimmed.substring(name.length + 1);
          }
        }
        return null;
      };

      const response = await fetch('/api/v1/settings/avatar/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'X-CSRFToken': getCsrfToken() || '',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || 'Failed to upload avatar');
      }

      const data = await response.json();
      setSuccess('Avatar uploaded successfully');
      await checkAuth(); // Refresh user data
      return data.avatar;
    } catch (err) {
      // Zobraz generickou zprávu, ne surový error
      setError('Nastala chyba při nahrávání avatara. Zkuste to prosím znovu.');
      if (import.meta.env.DEV) {
        console.error('Avatar upload error:', err);
      }
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [checkAuth]);

  /**
   * Update goals settings
   */
  const updateGoals = useCallback(async (data: GoalsSettings): Promise<boolean> => {
    const result = await handleRequest(
      () => api.patch('/settings/goals/', data),
      'Goals updated successfully'
    );
    if (result) {
      await checkAuth(); // Refresh user data
    }
    return result;
  }, [handleRequest, checkAuth]);

  /**
   * Update privacy settings
   */
  const updatePrivacy = useCallback(async (data: PrivacySettings): Promise<boolean> => {
    return handleRequest(
      () => api.patch('/settings/privacy/', data),
      'Privacy settings updated successfully'
    );
  }, [handleRequest]);

  /**
   * Change password
   */
  const changePassword = useCallback(async (data: ChangePasswordData): Promise<boolean> => {
    return handleRequest(
      () => api.post('/settings/change-password/', data),
      'Password changed successfully'
    );
  }, [handleRequest]);

  /**
   * Change email
   */
  const changeEmail = useCallback(async (data: ChangeEmailData): Promise<boolean> => {
    return handleRequest(
      () => api.post('/settings/change-email/', data),
      'Verification email sent to your new email address'
    );
  }, [handleRequest]);

  /**
   * Delete account
   */
  const deleteAccount = useCallback(async (data: DeleteAccountData): Promise<boolean> => {
    const result = await handleRequest(
      () => api.post('/settings/delete-account/', data),
      'Account deleted successfully'
    );
    if (result) {
      await logout();
    }
    return result;
  }, [handleRequest, logout]);

  return {
    isLoading,
    error,
    success,
    clearMessages,
    updateProfile,
    uploadAvatar,
    updateGoals,
    updatePrivacy,
    changePassword,
    changeEmail,
    deleteAccount,
  };
}
