import { cn } from '@/lib/utils';
import { ProgressBar } from '@/components/ui/ProgressBar';

export interface WordCountProps {
  current: number;
  goal?: number;
  showProgress?: boolean;
  className?: string;
}

export function WordCount({ current, goal, showProgress = false, className }: WordCountProps) {
  // Simple pluralization - in production, use i18n library
  const getWordLabel = (count: number, language: 'cs' | 'en' = 'cs'): string => {
    if (language === 'cs') {
      if (count === 1) return 'slovo';
      if (count >= 2 && count <= 4) return 'slova';
      return 'slov';
    }
    return count === 1 ? 'word' : 'words';
  };

  const wordLabel = getWordLabel(current);

  return (
    <div className={cn('w-full', className)}>
      <div className="flex items-baseline justify-between">
        <span className="theme-aware text-sm font-mono text-text-main">
          {goal ? (
            <>
              <span className={current >= goal ? 'text-green-500 font-bold' : ''}>{current}</span>
              {' / '}
              <span className="theme-aware text-text-muted">{goal}</span>
              {' '}
              {wordLabel}
            </>
          ) : (
            <>
              {current} {wordLabel}
            </>
          )}
        </span>
        {goal && (
          <span className="theme-aware text-xs font-mono text-text-muted">
            {Math.round((current / goal) * 100)}%
          </span>
        )}
      </div>
      {showProgress && goal && (
        <div className="mt-2">
          <ProgressBar value={current} max={goal} animated={current < goal} />
        </div>
      )}
    </div>
  );
}
