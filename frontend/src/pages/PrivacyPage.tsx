import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { LanguageToggle } from '@/components/ui/LanguageToggle';
import { Footer } from '@/components/landing/Footer';
import { SEO } from '@/components/SEO';

export function PrivacyPage() {
  const { t } = useLanguage();

  const sections = [
    { key: 'intro', title: t('legal.privacyPolicy.intro.title'), content: t('legal.privacyPolicy.intro.content') },
    { key: 'dataCollection', title: t('legal.privacyPolicy.dataCollection.title'), content: t('legal.privacyPolicy.dataCollection.content') },
    { key: 'encryption', title: t('legal.privacyPolicy.encryption.title'), content: t('legal.privacyPolicy.encryption.content') },
    { key: 'cookies', title: t('legal.privacyPolicy.cookies.title'), content: t('legal.privacyPolicy.cookies.content') },
    { key: 'rights', title: t('legal.privacyPolicy.rights.title'), content: t('legal.privacyPolicy.rights.content') },
    { key: 'contact', title: t('legal.privacyPolicy.contact.title'), content: t('legal.privacyPolicy.contact.content') },
  ];

  return (
    <div className="min-h-screen relative" style={{ backgroundColor: 'var(--color-bg-app)' }}>
      <SEO
        title="Privacy Policy"
        description="QuietPage Privacy Policy - how we handle and protect your data."
        canonicalUrl="/privacy"
      />
      {/* Fixed toggles in corners */}
      <LanguageToggle />
      <ThemeToggle />

      {/* Main content container */}
      <main className="max-w-3xl mx-auto px-6 py-16">
        {/* Back link */}
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-text-muted hover:text-accent transition-colors mb-12 theme-aware"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          <span className="text-sm uppercase tracking-wider">{t('auth.backToHome')}</span>
        </Link>

        {/* Title */}
        <h1 className="text-3xl md:text-4xl font-bold uppercase tracking-wider mb-12 text-text-main theme-aware">
          {t('legal.privacyPolicy.title')}
        </h1>

        {/* Sections */}
        <div className="space-y-10">
          {sections.map((section, index) => (
            <section key={section.key} className="border-2 border-border bg-bg-panel p-6 shadow-hard theme-aware">
              <h2 className="text-lg font-bold uppercase tracking-wider mb-4 text-text-main theme-aware">
                {index + 1}. {section.title}
              </h2>
              <p className="text-text-muted leading-relaxed theme-aware">
                {section.content}
              </p>
            </section>
          ))}
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
