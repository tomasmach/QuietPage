import { TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

export interface MoodTrendBadgeProps {
  trend: 'improving' | 'declining' | 'stable' | undefined;
}

const trendConfig = {
  improving: {
    icon: TrendingUp,
    colorClasses: 'text-green-600 bg-green-100 border-green-300 dark:text-green-400 dark:bg-green-900/30 dark:border-green-700',
  },
  declining: {
    icon: TrendingDown,
    colorClasses: 'text-red-600 bg-red-100 border-red-300 dark:text-red-400 dark:bg-red-900/30 dark:border-red-700',
  },
  stable: {
    icon: ArrowRight,
    colorClasses: 'text-text-muted bg-bg-panel border-border',
  },
} as const;

export function MoodTrendBadge({ trend }: MoodTrendBadgeProps) {
  const { t } = useLanguage();

  if (!trend) {
    return null;
  }

  const config = trendConfig[trend];
  const Icon = config.icon;
  const label = t(`statistics.moodTrend.${trend}`);

  return (
    <span
      className={`
        inline-flex items-center gap-1
        px-2 py-0.5
        border
        font-mono text-xs font-bold uppercase tracking-wide
        ${config.colorClasses}
      `}
      title={label}
    >
      <Icon size={12} strokeWidth={2.5} />
      <span>{label}</span>
    </span>
  );
}
