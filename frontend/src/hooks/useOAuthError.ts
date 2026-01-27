import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { useToast } from '@/contexts/ToastContext';

/**
 * Handle OAuth error states from URL query parameters.
 * Displays appropriate toast messages for OAuth cancellation or failure.
 */
export function useOAuthError(): void {
  const [searchParams] = useSearchParams();
  const { t } = useLanguage();
  const toast = useToast();

  useEffect(() => {
    const error = searchParams.get('error');
    if (error === 'oauth_cancelled') {
      toast.error(t('auth.oauthCancelled'));
    } else if (error === 'oauth_failed') {
      toast.error(t('auth.oauthFailed'));
    }
  }, [searchParams, toast, t]);
}
