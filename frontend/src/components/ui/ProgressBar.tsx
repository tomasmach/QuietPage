import { type HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import { useLanguage } from '@/contexts/LanguageContext';

export interface ProgressBarProps extends Omit<HTMLAttributes<HTMLDivElement>, 'children'> {
  value: number;
  max?: number;
  showLabel?: boolean;
  animated?: boolean;
}

export function ProgressBar({
  value,
  max = 100,
  showLabel = true,
  animated = true,
  className,
  ...props
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const { t } = useLanguage();

  return (
    <div className={cn('w-full', className)} {...props}>
      {showLabel && (
        <div className="flex justify-between text-sm font-bold uppercase mb-1 text-text-main theme-aware">
          <span>{t('meta.progress')}</span>
          <span>{value} / {max} {t('meta.wordsSuffix')}</span>
        </div>
      )}
      <div
        className="h-4 w-full border-2 border-border bg-bg-panel relative theme-aware"
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={showLabel ? `Progress: ${Math.round(percentage)}%` : undefined}
      >
        <div
          className={cn(
            'h-full transition-all duration-500 bg-accent theme-aware',
            animated && percentage < 100 && 'progress-striped'
          )}
          style={{ width: `${percentage}%` }}
        />
        {percentage >= 100 && (
          <div className="absolute inset-0 flex items-center justify-center text-xs font-bold uppercase tracking-widest text-accent-fg theme-aware">
            {t('meta.goalMet')}
          </div>
        )}
      </div>
    </div>
  );
}
