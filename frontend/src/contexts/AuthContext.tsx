import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { api } from '../lib/api';
import { useTheme } from './ThemeContext';
import { useLanguage } from './LanguageContext';
import type { Theme } from './ThemeContext';
import type { Language } from './LanguageContext';

interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  avatar?: string;
  bio?: string;
  timezone: string;
  daily_word_goal: number;
  preferred_writing_time?: 'morning' | 'afternoon' | 'evening';
  reminder_enabled?: boolean;
  reminder_time?: string;
  email_notifications?: boolean;
  current_streak: number;
  longest_streak: number;
  preferred_language?: Language;
  preferred_theme?: Theme;
}

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const { syncFromAPI: syncTheme } = useTheme();
  const { syncFromAPI: syncLanguage } = useLanguage();

  const isAuthenticated = user !== null;

  /**
   * Sync theme and language preferences from user data
   */
  const syncPreferences = useCallback((userData: User) => {
    if (userData.preferred_theme) {
      syncTheme(userData.preferred_theme);
    }
    if (userData.preferred_language) {
      syncLanguage(userData.preferred_language);
    }
  }, [syncTheme, syncLanguage]);

  /**
   * Fetch current user from API
   */
  const checkAuth = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.get<{ user: User }>('/auth/me/');
      setUser(response.user);
      syncPreferences(response.user);
    } catch {
      // User not authenticated or error occurred
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [syncPreferences]);

  /**
   * Check authentication status on mount
   * Wait for API client to be ready (CSRF token fetched) before checking auth
   */
  useEffect(() => {
    const initAuth = async () => {
      await api.ready();
      await checkAuth();
    };
    initAuth();
  }, [checkAuth]);

  /**
   * Login user
   */
  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    try {
      // API expects username_or_email field
      const payload = {
        username_or_email: credentials.username,
        password: credentials.password,
      };
      const response = await api.post<{ user: User }>('/auth/login/', payload);
      setUser(response.user);
      syncPreferences(response.user);
    } catch (error) {
      setIsLoading(false);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Logout user
   */
  const logout = async () => {
    setIsLoading(true);
    try {
      await api.post('/auth/logout/');
      setUser(null);
    } catch (error) {
      // Even if logout fails, clear user state
      setUser(null);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Register new user
   */
  const register = async (credentials: RegisterCredentials) => {
    setIsLoading(true);
    try {
      const response = await api.post<{ user: User }>('/auth/register/', credentials);
      setUser(response.user);
      syncPreferences(response.user);
    } catch (error) {
      setIsLoading(false);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextValue = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    register,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
