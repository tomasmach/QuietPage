import { Link } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { Logo } from '@/components/ui/Logo';

export function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="theme-aware border-t-2 border-border mt-20">
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Main footer content - 3 columns on desktop, stacked on mobile */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-8">
          {/* Column 1: Logo */}
          <div className="flex flex-col items-center md:items-start">
            <Logo size="sm" />
          </div>

          {/* Column 2: Links */}
          <div className="flex flex-col items-center md:items-start">
            <h3 className="theme-aware text-sm font-bold uppercase tracking-wider mb-4 text-text-main">
              {t('footer.links')}
            </h3>
            <nav className="flex flex-col gap-2">
              <Link
                to="/terms"
                className="theme-aware text-sm text-text-muted hover:text-accent transition-colors"
              >
                {t('footer.termsOfService')}
              </Link>
              <Link
                to="/privacy"
                className="theme-aware text-sm text-text-muted hover:text-accent transition-colors"
              >
                {t('footer.privacyPolicy')}
              </Link>
            </nav>
          </div>

          {/* Column 3: Contact */}
          <div className="flex flex-col items-center md:items-start">
            <h3 className="theme-aware text-sm font-bold uppercase tracking-wider mb-4 text-text-main">
              {t('footer.contact')}
            </h3>
            <a
              href="mailto:tomades1@gmail.com"
              className="theme-aware text-sm text-text-muted hover:text-accent transition-colors"
            >
              tomades1@gmail.com
            </a>
          </div>
        </div>

        {/* Copyright line */}
        <div className="theme-aware border-t-2 border-dashed border-border mt-10 pt-6 text-center">
          <p className="theme-aware text-sm text-text-muted">
            {t('footer.copyright')}
          </p>
        </div>
      </div>
    </footer>
  );
}
