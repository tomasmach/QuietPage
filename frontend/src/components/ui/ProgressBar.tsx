import { type HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface ProgressBarProps extends Omit<HTMLAttributes<HTMLDivElement>, 'children'> {
  value: number;
  max?: number;
  showLabel?: boolean;
  animated?: boolean;
}

export function ProgressBar({
  value,
  max = 100,
  showLabel = false,
  animated = false,
  className,
  ...props
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={cn('w-full', className)} {...props}>
      <div
        className="h-4 border-2 border-border bg-bg-panel overflow-hidden relative"
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={showLabel ? `Progress: ${Math.round(percentage)}%` : undefined}
      >
        <div
          className={cn(
            'h-full bg-accent transition-all duration-300',
            animated && 'progress-striped'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="mt-1 text-xs text-text-muted font-mono text-right">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
}
