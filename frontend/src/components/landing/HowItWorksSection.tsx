import { Pencil, BarChart2, TrendingUp } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

interface StepCardProps {
  number: number;
  icon: React.ReactNode;
  title: string;
  description: string;
}

const StepCard: React.FC<StepCardProps> = ({ number, icon, title, description }) => {
  return (
    <div className="theme-aware bg-bg-panel border-2 border-border p-6 shadow-hard transition-all duration-150 hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_var(--color-shadow)]">
      {/* Header: Number + Title on left, Icon on right */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl font-bold text-accent">{number}.</span>
          <h3 className="text-lg font-bold uppercase tracking-wider text-text-main">
            {title}
          </h3>
        </div>
        <div className="text-accent">{icon}</div>
      </div>

      {/* Description */}
      <p className="text-sm text-text-muted leading-relaxed">
        {description}
      </p>
    </div>
  );
};

export const HowItWorksSection: React.FC = () => {
  const { t } = useLanguage();

  const steps = [
    {
      number: 1,
      icon: <Pencil size={32} />,
      title: t('landing.howItWorks.step1.title'),
      description: t('landing.howItWorks.step1.description'),
    },
    {
      number: 2,
      icon: <BarChart2 size={32} />,
      title: t('landing.howItWorks.step2.title'),
      description: t('landing.howItWorks.step2.description'),
    },
    {
      number: 3,
      icon: <TrendingUp size={32} />,
      title: t('landing.howItWorks.step3.title'),
      description: t('landing.howItWorks.step3.description'),
    },
  ];

  return (
    <section className="mb-20">
      {/* Section title */}
      <h2 className="text-2xl md:text-3xl font-bold uppercase tracking-wider mb-8 text-text-main text-center">
        {t('landing.howItWorks.title')}
      </h2>

      {/* Steps grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {steps.map((step) => (
          <StepCard
            key={step.number}
            number={step.number}
            icon={step.icon}
            title={step.title}
            description={step.description}
          />
        ))}
      </div>
    </section>
  );
};
