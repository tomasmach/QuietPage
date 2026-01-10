import { type LucideIcon } from 'lucide-react';
import { type ReactNode } from 'react';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  visual?: ReactNode;
  iconAnimation?: 'float' | 'pulse' | 'flicker' | 'none';
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon: Icon,
  title,
  description,
  visual,
  iconAnimation = 'none',
}) => {
  const animationClass = {
    float: 'float-animation',
    pulse: 'pulse-animation',
    flicker: 'flicker-animation',
    none: '',
  }[iconAnimation];

  const animationStyle = {
    float: { animation: 'float 3s ease-in-out infinite' },
    pulse: { animation: 'pulse-subtle 2s ease-in-out infinite' },
    flicker: { animation: 'flicker 1.5s ease-in-out infinite' },
    none: {},
  }[iconAnimation];

  return (
    <div className="theme-aware bg-bg-panel border-2 border-border p-6 transition-all duration-150 hover:translate-x-[2px] hover:translate-y-[2px] shadow-hard hover:shadow-[2px_2px_0px_0px_var(--color-shadow)]">
      {/* Icon */}
      <div
        className={`mb-4 ${animationClass}`}
        style={animationStyle}
      >
        <Icon size={40} className="theme-aware text-accent" />
      </div>

      {/* Title */}
      <h3 className="theme-aware text-lg font-bold uppercase tracking-wider mb-3 text-text-main">
        {title}
      </h3>

      {/* Description */}
      <p className="theme-aware text-sm text-text-muted mb-4 leading-relaxed">
        {description}
      </p>

      {/* Optional Visual Element */}
      {visual && (
        <div className="theme-aware mt-4 pt-4 border-t-2 border-dashed border-border">
          {visual}
        </div>
      )}
    </div>
  );
};
