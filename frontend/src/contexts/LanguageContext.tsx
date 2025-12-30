import { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { translations } from '../locales';
import type { Language } from '../locales';
import { api } from '../lib/api';

export type { Language } from '../locales';

type TranslationKey = string;
type TranslationParams = Record<string, string | number>;

interface LanguageContextValue {
  language: Language;
  setLanguage: (language: Language) => void;
  syncFromAPI: (language: Language) => void;
  t: (key: TranslationKey, params?: TranslationParams) => string;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

const LANGUAGE_STORAGE_KEY = 'quietpage-language';

interface LanguageProviderProps {
  children: ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [language, setLanguageState] = useState<Language>(() => {
    // Get language from localStorage or default to 'cs'
    const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
    return (stored === 'cs' || stored === 'en') ? stored : 'cs';
  });

  /**
   * Set language from API without saving back to API (avoids circular calls)
   * Used by AuthContext when user data is loaded
   */
  const syncFromAPI = useCallback((newLanguage: Language) => {
    setLanguageState(newLanguage);
    localStorage.setItem(LANGUAGE_STORAGE_KEY, newLanguage);
  }, []);

  /**
   * Set language with persistence to localStorage and API (if authenticated)
   * Used for user-initiated language changes
   */
  const setLanguage = useCallback((newLanguage: Language) => {
    setLanguageState(newLanguage);
    localStorage.setItem(LANGUAGE_STORAGE_KEY, newLanguage);

    // Save to API (fire and forget - don't block UI)
    api.patch('/settings/profile/', { preferred_language: newLanguage }).catch(() => {
      // Silently ignore errors - user may not be authenticated
    });
  }, []);

  /**
   * Translation function
   * Supports nested keys using dot notation (e.g., 'nav.write')
   * Supports template parameters (e.g., t('key', { name: 'John' }) replaces {name} with John)
   */
  const t = (key: TranslationKey, params?: TranslationParams): string => {
    const keys = key.split('.');
    let value: unknown = translations[language];

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = (value as Record<string, unknown>)[k];
      } else {
        // Fallback to key if translation not found
        console.warn(`Translation key not found: ${key}`);
        return key;
      }
    }

    let result = typeof value === 'string' ? value : key;

    // Replace template parameters
    if (params) {
      Object.entries(params).forEach(([paramKey, paramValue]) => {
        result = result.replace(new RegExp(`\\{${paramKey}\\}`, 'g'), String(paramValue));
      });
    }

    return result;
  };

  const value: LanguageContextValue = {
    language,
    setLanguage,
    syncFromAPI,
    t,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useLanguage(): LanguageContextValue {
  const context = useContext(LanguageContext);

  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }

  return context;
}
