import { useLanguage } from '@/contexts/LanguageContext';

export const StorytellingSection: React.FC = () => {
  const { t } = useLanguage();

  return (
    <section className="mb-20">
      <div className="theme-aware bg-bg-panel border-2 border-border shadow-hard p-8 md:p-12">
        <div className="max-w-3xl mx-auto text-center">
          {/* Headline */}
          <h2 className="text-2xl md:text-3xl font-bold uppercase tracking-wider mb-8 text-text-main">
            {t('landing.storytelling.headline')}
          </h2>

          {/* Body paragraphs */}
          <div className="space-y-6">
            <p className="text-base md:text-lg text-text-muted leading-relaxed">
              {t('landing.storytelling.p1')}
            </p>
            <p className="text-base md:text-lg text-text-muted leading-relaxed">
              {t('landing.storytelling.p2')}
            </p>
            <p className="text-base md:text-lg text-text-muted leading-relaxed">
              {t('landing.storytelling.p3')}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
