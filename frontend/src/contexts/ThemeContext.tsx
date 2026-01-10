import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { api } from '../lib/api';

export type Theme = 'midnight' | 'paper';

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  syncFromAPI: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

const THEME_STORAGE_KEY = 'quietpage-theme';

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(() => {
    // Get theme from localStorage or default to 'midnight'
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    return (stored === 'midnight' || stored === 'paper') ? stored : 'midnight';
  });

  useEffect(() => {
    // Set data-theme attribute on <html> element
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  /**
   * Set theme from API without saving back to API (avoids circular calls)
   * Used by AuthContext when user data is loaded
   */
  const syncFromAPI = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem(THEME_STORAGE_KEY, newTheme);
  }, []);

  /**
   * Set theme with persistence to localStorage and API (if authenticated)
   * Used for user-initiated theme changes
   */
  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem(THEME_STORAGE_KEY, newTheme);

    // Save to API only if user is authenticated
    if (api.isAuthenticated) {
      api.patch('/settings/profile/', { preferred_theme: newTheme }).catch(() => {
        // Silently ignore errors
      });
    }
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState(prev => {
      const newTheme = prev === 'midnight' ? 'paper' : 'midnight';
      localStorage.setItem(THEME_STORAGE_KEY, newTheme);

      // Save to API only if user is authenticated
      if (api.isAuthenticated) {
        api.patch('/settings/profile/', { preferred_theme: newTheme }).catch(() => {
          // Silently ignore errors
        });
      }

      return newTheme;
    });
  }, []);

  const value: ThemeContextValue = {
    theme,
    setTheme,
    toggleTheme,
    syncFromAPI,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }

  return context;
}
