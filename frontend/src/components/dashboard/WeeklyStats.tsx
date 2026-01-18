import { Flame, Calendar, Trophy } from 'lucide-react';
import type { WeeklyStats as WeeklyStatsType } from '../../hooks/useDashboard';
import { useLanguage } from '../../contexts/LanguageContext';
import { cn } from '../../lib/utils';

interface WeeklyStatsProps {
  weeklyStats: WeeklyStatsType | null;
  currentStreak: number;
}

/**
 * Format a number with locale-aware separators
 * Czech uses space as thousands separator, English uses comma
 */
function formatNumber(num: number, locale: string): string {
  return num.toLocaleString(locale === 'cs' ? 'cs-CZ' : 'en-US');
}

/**
 * WeeklyStats component displays 3 statistics in a vertical layout:
 * - Current streak (days)
 * - Words written this week
 * - Best day this week (words and weekday)
 */
export function WeeklyStats({ weeklyStats, currentStreak }: WeeklyStatsProps) {
  const { t, language } = useLanguage();

  // Translate weekday from English API response to localized name
  const getWeekdayName = (weekday: string): string => {
    const key = `weekdays.${weekday.toLowerCase()}`;
    return t(key);
  };

  return (
    <div className="space-y-4">
      {/* Current Streak */}
      <div className={cn('border-2 border-border p-4 bg-bg-panel shadow-hard theme-aware')}>
        <div className="flex items-center gap-2 mb-2">
          <Flame size={14} className={cn('text-text-main theme-aware')} />
          <span className={cn('text-xs font-bold uppercase text-text-muted theme-aware')}>
            {t('dashboard.weeklyStats.streak')}
          </span>
        </div>
        <div className={cn('text-2xl font-bold text-text-main theme-aware')}>
          {t('dashboard.weeklyStats.streakDays', { count: currentStreak })}
        </div>
      </div>

      {/* Words This Week */}
      <div className={cn('border-2 border-border p-4 bg-bg-panel shadow-hard theme-aware')}>
        <div className="flex items-center gap-2 mb-2">
          <Calendar size={14} className={cn('text-text-main theme-aware')} />
          <span className={cn('text-xs font-bold uppercase text-text-muted theme-aware')}>
            {t('dashboard.weeklyStats.thisWeek')}
          </span>
        </div>
        <div className={cn('text-2xl font-bold text-text-main theme-aware')}>
          {weeklyStats
            ? t('dashboard.weeklyStats.words', {
                count: formatNumber(weeklyStats.totalWords, language),
              })
            : t('dashboard.weeklyStats.words', { count: 0 })}
        </div>
      </div>

      {/* Best Day This Week */}
      {weeklyStats?.bestDay && (
        <div className={cn('border-2 border-border p-4 bg-bg-panel shadow-hard theme-aware')}>
          <div className="flex items-center gap-2 mb-2">
            <Trophy size={14} className={cn('text-text-main theme-aware')} />
            <span className={cn('text-xs font-bold uppercase text-text-muted theme-aware')}>
              {t('dashboard.weeklyStats.bestDay')}
            </span>
          </div>
          <div className={cn('text-2xl font-bold text-text-main theme-aware')}>
            {t('dashboard.weeklyStats.words', {
              count: formatNumber(weeklyStats.bestDay.words, language),
            })}
          </div>
          <div className={cn('text-sm text-text-muted mt-1 theme-aware')}>
            {getWeekdayName(weeklyStats.bestDay.weekday)}
          </div>
        </div>
      )}
    </div>
  );
}
