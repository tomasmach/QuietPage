import { Link } from 'react-router-dom';
import { Lock, TrendingUp, Target } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Logo } from '@/components/ui/Logo';
import { Button } from '@/components/ui/Button';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { LanguageToggle } from '@/components/ui/LanguageToggle';

export function HomePage() {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-bg-main flex items-center justify-center p-8 relative">
      {/* Fixed toggles in corners */}
      <LanguageToggle />
      <ThemeToggle />

      {/* Main content */}
      <div className="max-w-4xl w-full">
        {/* Hero section */}
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <Logo size="lg" />
          </div>
          <h1 className="text-5xl font-bold text-text-main font-mono mb-4">
            {t('landing.title')}
          </h1>
          <p className="text-xl text-text-muted font-mono">
            {t('landing.tagline')}
          </p>
        </div>

        {/* Features grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {/* Feature 1: Encryption */}
          <div className="bg-bg-panel border-2 border-border shadow-hard p-6">
            <div className="mb-4 inline-flex p-3 bg-accent/10 border-2 border-border">
              <Lock size={28} className="text-accent" />
            </div>
            <h3 className="text-lg font-bold text-text-main font-mono mb-2 uppercase">
              {t('landing.features.encrypted.title')}
            </h3>
            <p className="text-sm text-text-muted font-mono">
              {t('landing.features.encrypted.description')}
            </p>
          </div>

          {/* Feature 2: Progress */}
          <div className="bg-bg-panel border-2 border-border shadow-hard p-6">
            <div className="mb-4 inline-flex p-3 bg-accent/10 border-2 border-border">
              <TrendingUp size={28} className="text-accent" />
            </div>
            <h3 className="text-lg font-bold text-text-main font-mono mb-2 uppercase">
              {t('landing.features.progress.title')}
            </h3>
            <p className="text-sm text-text-muted font-mono">
              {t('landing.features.progress.description')}
            </p>
          </div>

          {/* Feature 3: Goals */}
          <div className="bg-bg-panel border-2 border-border shadow-hard p-6">
            <div className="mb-4 inline-flex p-3 bg-accent/10 border-2 border-border">
              <Target size={28} className="text-accent" />
            </div>
            <h3 className="text-lg font-bold text-text-main font-mono mb-2 uppercase">
              {t('landing.features.goals.title')}
            </h3>
            <p className="text-sm text-text-muted font-mono">
              {t('landing.features.goals.description')}
            </p>
          </div>
        </div>

        {/* CTA buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/signup">
            <Button variant="primary" size="lg" className="w-full sm:w-auto">
              {t('landing.getStarted')}
            </Button>
          </Link>
          <Link to="/login">
            <Button variant="secondary" size="lg" className="w-full sm:w-auto">
              {t('landing.signIn')}
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
