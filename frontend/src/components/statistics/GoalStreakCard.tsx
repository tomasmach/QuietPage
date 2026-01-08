/**
 * GoalStreakCard displays the prestigious 750-word goal streak.
 *
 * Features:
 * - Prominent display of current goal streak with flame icon
 * - Longest (all-time) goal streak record
 * - Clear visual distinction from regular entry streaks
 * - Goal value display (e.g., "750 words/day")
 * - Motivational messaging based on streak status
 * - Brutalist design with solid colors and hard borders
 */

import { Flame, Target } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';
import type { GoalStreak } from '../../types/statistics';

export interface GoalStreakCardProps {
  data: GoalStreak | undefined;
}

export function GoalStreakCard({ data }: GoalStreakCardProps) {
  const { t, language } = useLanguage();

  // Empty state - no data yet
  if (!data) {
    return (
      <div className="border-2 border-border bg-bg-panel p-6 rounded-none shadow-hard">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 border-2 border-border bg-bg-app">
            <Target size={20} strokeWidth={2} className="text-text-muted" />
          </div>
          <h3 className="text-xs font-bold uppercase tracking-widest text-text-main font-mono">
            {t('statistics.goalStreak.title')}
          </h3>
        </div>
        <p className="text-sm font-mono text-text-muted">
          {t('statistics.goalStreak.inactive')}
        </p>
      </div>
    );
  }

  const hasActiveStreak = data.current > 0;
  const isNewRecord = data.current > 0 && data.current >= data.longest;

  // Format numbers according to locale
  const formatNumber = (num: number) => {
    return num.toLocaleString(language === 'cs' ? 'cs-CZ' : 'en-US');
  };

  // Get days label
  const daysLabel = t('statistics.goalStreak.days');

  return (
    <div
      className={`
        border-2 p-6 rounded-none shadow-hard relative overflow-hidden
        ${hasActiveStreak
          ? 'border-accent bg-accent text-accent-fg'
          : 'border-border bg-bg-panel text-text-main'
        }
      `}
    >
      {/* Decorative background flame for active streaks */}
      {hasActiveStreak && (
        <div className="absolute top-0 right-0 opacity-10 pointer-events-none">
          <Flame size={140} strokeWidth={1} className="translate-x-8 -translate-y-4" />
        </div>
      )}

      {/* Header with Flame icon */}
      <div className="flex items-center gap-3 mb-4 relative">
        <div
          className={`
            p-2 border-2
            ${hasActiveStreak
              ? 'border-current bg-accent-fg/10'
              : 'border-border bg-bg-app'
            }
          `}
        >
          <Flame
            size={20}
            strokeWidth={2}
            className={hasActiveStreak ? '' : 'text-text-muted'}
          />
        </div>
        <h3 className="text-xs font-bold uppercase tracking-widest font-mono">
          {t('statistics.goalStreak.title')}
        </h3>
      </div>

      {/* Goal value */}
      <p
        className={`
          text-sm font-mono mb-4 relative
          ${hasActiveStreak ? 'opacity-80' : 'text-text-muted'}
        `}
      >
        {formatNumber(data.goal)} {t('statistics.goalStreak.perDay')}
      </p>

      {/* Streak stats */}
      <div className="flex gap-6 relative mb-4">
        {/* Current Streak */}
        <div>
          <p className="text-4xl font-bold font-mono">
            {formatNumber(data.current)}
          </p>
          <p
            className={`
              text-xs font-mono uppercase tracking-wider
              ${hasActiveStreak ? 'opacity-80' : 'text-text-muted'}
            `}
          >
            {t('statistics.goalStreak.current')} {daysLabel}
          </p>
        </div>

        {/* Longest Streak */}
        <div
          className={`
            border-l-2 pl-6
            ${hasActiveStreak ? 'border-current opacity-80' : 'border-border'}
          `}
        >
          <p className="text-4xl font-bold font-mono">
            {formatNumber(data.longest)}
          </p>
          <p
            className={`
              text-xs font-mono uppercase tracking-wider
              ${hasActiveStreak ? 'opacity-80' : 'text-text-muted'}
            `}
          >
            {t('statistics.goalStreak.longest')} {daysLabel}
          </p>
        </div>
      </div>

      {/* Motivational message */}
      <div
        className={`
          pt-3 border-t-2 relative
          ${hasActiveStreak ? 'border-current' : 'border-border'}
        `}
      >
        <p className="text-sm font-mono font-bold">
          {hasActiveStreak
            ? t('statistics.goalStreak.active')
            : t('statistics.goalStreak.inactive')
          }
        </p>
        {isNewRecord && hasActiveStreak && (
          <p className="text-xs font-mono opacity-80 mt-1 uppercase tracking-wider">
            {t('statistics.streakHistory.newRecord', { days: data.current })}
          </p>
        )}
      </div>
    </div>
  );
}
