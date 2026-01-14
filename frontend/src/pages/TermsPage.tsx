import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { LanguageToggle } from '@/components/ui/LanguageToggle';
import { Footer } from '@/components/landing/Footer';
import { SEO } from '@/components/SEO';

export function TermsPage() {
  const { t } = useLanguage();

  const sections = [
    { key: 'intro', title: t('legal.termsOfService.intro.title'), content: t('legal.termsOfService.intro.content') },
    { key: 'service', title: t('legal.termsOfService.service.title'), content: t('legal.termsOfService.service.content') },
    { key: 'accounts', title: t('legal.termsOfService.accounts.title'), content: t('legal.termsOfService.accounts.content') },
    { key: 'content', title: t('legal.termsOfService.content.title'), content: t('legal.termsOfService.content.content') },
    { key: 'limitations', title: t('legal.termsOfService.limitations.title'), content: t('legal.termsOfService.limitations.content') },
    { key: 'changes', title: t('legal.termsOfService.changes.title'), content: t('legal.termsOfService.changes.content') },
    { key: 'contact', title: t('legal.termsOfService.contact.title'), content: t('legal.termsOfService.contact.content') },
  ];

  return (
    <div className="min-h-screen relative" style={{ backgroundColor: 'var(--color-bg-app)' }}>
      <SEO
        title="Terms of Service"
        description="Read the Terms of Service for QuietPage, your private mindful writing and journaling application."
        canonicalUrl="/terms"
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
          {t('legal.termsOfService.title')}
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
