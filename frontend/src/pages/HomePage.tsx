import { Link } from 'react-router-dom';
import { Shield, Heart, Flame, BarChart3, Lock, Shield as ShieldCheck } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Logo } from '@/components/ui/Logo';
import { Button } from '@/components/ui/Button';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { LanguageToggle } from '@/components/ui/LanguageToggle';
import { FeatureCard } from '@/components/landing/FeatureCard';
import { TrustBadge } from '@/components/landing/TrustBadge';

export function HomePage() {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen relative" style={{ backgroundColor: 'var(--color-bg-app)' }}>
      {/* Fixed toggles in corners */}
      <LanguageToggle />
      <ThemeToggle />

      {/* Main content container */}
      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* SECTION 1: HERO */}
        <section className="text-center mb-20">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <Logo size="lg" />
          </div>

          {/* Headline */}
          <h1 className="text-4xl md:text-5xl font-bold uppercase tracking-wider mb-4 text-text-main">
            {t('landing.hero.headline')}
          </h1>

          {/* Subheadline */}
          <p className="text-lg md:text-xl text-text-muted mb-10 max-w-3xl mx-auto leading-relaxed">
            {t('landing.hero.subheadline')}
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
            <Link to="/signup">
              <Button variant="primary" size="lg" className="w-full sm:w-auto min-w-[200px]">
                {t('landing.getStarted')}
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="secondary" size="lg" className="w-full sm:w-auto min-w-[200px]">
                {t('landing.signIn')}
              </Button>
            </Link>
          </div>

          {/* Small trust indicator */}
          <div className="flex justify-center">
            <TrustBadge icon={Lock} text={t('landing.trust.encrypted')} />
          </div>
        </section>

        {/* SECTION 2: FEATURES */}
        <section className="mb-20">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Feature 1: Privacy */}
            <FeatureCard
              icon={Shield}
              title={t('landing.features.privacy.title')}
              description={t('landing.features.privacy.description')}
            />

            {/* Feature 2: Mood Tracking */}
            <FeatureCard
              icon={Heart}
              title={t('landing.features.moodTracking.title')}
              description={t('landing.features.moodTracking.description')}
            />

            {/* Feature 3: Streaks */}
            <FeatureCard
              icon={Flame}
              title={t('landing.features.streaks.title')}
              description={t('landing.features.streaks.description')}
            />

            {/* Feature 4: Insights */}
            <FeatureCard
              icon={BarChart3}
              title={t('landing.features.insights.title')}
              description={t('landing.features.insights.description')}
            />
          </div>
        </section>

        {/* SECTION 3: FINAL CTA */}
        <section className="text-center">
          {/* Container with subtle accent background */}
          <div className="bg-bg-panel border-2 border-border shadow-hard p-10 md:p-12">
            {/* Headline */}
            <h2 className="text-3xl md:text-4xl font-bold uppercase tracking-wider mb-4 text-text-main">
              {t('landing.finalCta.headline')}
            </h2>

            {/* Subtext */}
            <p className="text-lg text-text-muted mb-8">
              {t('landing.finalCta.subtext')}
            </p>

            {/* CTA Buttons (same as hero) */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Link to="/signup">
                <Button variant="primary" size="lg" className="w-full sm:w-auto min-w-[200px]">
                  {t('landing.getStarted')}
                </Button>
              </Link>
              <Link to="/login">
                <Button variant="secondary" size="lg" className="w-full sm:w-auto min-w-[200px]">
                  {t('landing.signIn')}
                </Button>
              </Link>
            </div>

            {/* Trust badges row */}
            <div className="flex flex-wrap gap-3 justify-center">
              <TrustBadge icon={Lock} text={t('landing.trust.encrypted')} />
              <TrustBadge icon={ShieldCheck} text={t('landing.trust.private')} />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
