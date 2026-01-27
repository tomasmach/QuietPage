import { useLanguage } from '@/contexts/LanguageContext';

/**
 * Visual divider between OAuth buttons and traditional login form.
 */
export function OAuthDivider() {
  const { t } = useLanguage();

  return (
    <div className="flex items-center gap-4 my-6">
      <div className="flex-1 h-px bg-border" />
      <span className="text-text-muted text-sm font-mono">{t('auth.or')}</span>
      <div className="flex-1 h-px bg-border" />
    </div>
  );
}
