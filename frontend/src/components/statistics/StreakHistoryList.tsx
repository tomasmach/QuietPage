/**
 * StreakHistoryList component displays top 5 historical streaks.
 * 
 * Features:
 * - Shows start date, end date, and length of each streak
 * - Highlights the longest streak with special styling
 * - Marks current active streak (if in top 5)
 * - Gamified encouragement messaging
 * - Follows brutalist design system (hard shadows, sharp borders, monospace)
 */

import { useMemo } from 'react';
import { TrendingUp, Award } from 'lucide-react';
import type { WritingPatterns } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';
import { useAuth } from '../../contexts/AuthContext';

interface StreakHistoryListProps {
  data: WritingPatterns;
}

interface StreakItem {
  startDate: string;
  endDate: string;
  length: number;
  isLongest: boolean;
  isCurrent: boolean;
}

/**
 * Formats a date string to localized format (e.g., "Dec 1, 2025")
 */
function formatDate(dateString: string, language: 'cs' | 'en'): string {
  const date = new Date(dateString);
  const options: Intl.DateTimeFormatOptions = {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  };
  
  return date.toLocaleDateString(language === 'cs' ? 'cs-CZ' : 'en-US', options);
}

/**
 * Checks if a streak is currently active by comparing end date with today
 */
function isStreakCurrent(endDateString: string): boolean {
  const endDate = new Date(endDateString);
  const today = new Date();
  
  // Normalize to date only (ignore time)
  endDate.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);
  
  // A streak is current if it ended today or yesterday (grace period)
  const daysDiff = Math.floor((today.getTime() - endDate.getTime()) / (1000 * 60 * 60 * 24));
  
  return daysDiff <= 1;
}

export function StreakHistoryList({ data }: StreakHistoryListProps) {
  const { t, language } = useLanguage();
  const { user } = useAuth();
  
  // Process and sort streaks
  const streakItems: StreakItem[] = useMemo(() => {
    if (!data.streakHistory || data.streakHistory.length === 0) {
      return [];
    }
    
    // Find longest streak
    const maxLength = Math.max(...data.streakHistory.map(s => s.length));
    
    // Map and sort streaks (top 5)
    return data.streakHistory
      .map(streak => ({
        startDate: streak.startDate,
        endDate: streak.endDate,
        length: streak.length,
        isLongest: streak.length === maxLength,
        isCurrent: isStreakCurrent(streak.endDate),
      }))
      .sort((a, b) => b.length - a.length)
      .slice(0, 5);
  }, [data.streakHistory]);
  
  // No data state
  if (streakItems.length === 0) {
    return (
      <div className="border-2 border-border bg-bg-panel p-8 text-center rounded-none shadow-hard">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
          {t('statistics.streakHistory.title')}
        </h3>
        <p className="text-text-muted font-mono text-sm">
          {t('statistics.streakHistory.noData')}
        </p>
      </div>
    );
  }
  
  const longestStreak = streakItems.find(s => s.isLongest);
  const currentStreak = user?.current_streak || 0;
  
  return (
    <div className="border-2 border-border bg-bg-panel rounded-none shadow-hard">
      {/* Header */}
      <div className="border-b-2 border-border p-6">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-main font-mono">
          {t('statistics.streakHistory.title')}
        </h3>
      </div>
      
      {/* Streak List */}
      <div className="divide-y-2 divide-border">
        {streakItems.map((streak, index) => (
          <div
            key={`${streak.startDate}-${streak.endDate}`}
            className={`
              p-6 transition-all duration-150
              ${streak.isLongest 
                ? 'bg-accent text-accent-fg hover:translate-x-[2px] hover:translate-y-[2px]' 
                : 'bg-bg-panel hover:bg-bg-app'
              }
            `}
          >
            <div className="flex items-start justify-between gap-4">
              {/* Date Range and Length */}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  {/* Rank number */}
                  <span className={`
                    text-xs font-bold font-mono
                    ${streak.isLongest ? 'text-accent-fg' : 'text-text-muted'}
                  `}>
                    #{index + 1}
                  </span>
                  
                  {/* Longest badge */}
                  {streak.isLongest && (
                    <div className="flex items-center gap-1 px-2 py-1 border-2 border-current rounded-none">
                      <Award size={12} strokeWidth={2} />
                      <span className="text-xs font-bold uppercase tracking-wider font-mono">
                        {t('statistics.streakHistory.longest')}
                      </span>
                    </div>
                  )}
                  
                  {/* Current streak badge */}
                  {streak.isCurrent && (
                    <div className={`
                      flex items-center gap-1 px-2 py-1 border-2 rounded-none
                      ${streak.isLongest ? 'border-accent-fg' : 'border-accent'}
                    `}>
                      <TrendingUp size={12} strokeWidth={2} />
                      <span className={`
                        text-xs font-bold uppercase tracking-wider font-mono
                        ${streak.isLongest ? 'text-accent-fg' : 'text-accent'}
                      `}>
                        {t('statistics.streakHistory.current')}
                      </span>
                    </div>
                  )}
                </div>
                
                {/* Date range */}
                <p className={`
                  text-sm font-mono mb-1
                  ${streak.isLongest ? 'text-accent-fg' : 'text-text-main'}
                `}>
                  {formatDate(streak.startDate, language)} – {formatDate(streak.endDate, language)}
                </p>
              </div>
              
              {/* Streak length */}
              <div className="text-right">
                <p className={`
                  text-2xl font-bold font-mono
                  ${streak.isLongest ? 'text-accent-fg' : 'text-text-main'}
                `}>
                  {streak.length}
                </p>
                <p className={`
                  text-xs font-mono
                  ${streak.isLongest ? 'text-accent-fg opacity-80' : 'text-text-muted'}
                `}>
                  {streak.length === 1 
                    ? t('statistics.streakHistory.daySingular')
                    : t('statistics.streakHistory.daysPlural')}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Gamification Footer */}
      {longestStreak && (
        <div className="border-t-2 border-border p-6 bg-bg-app">
          <p className="text-sm font-mono text-text-main">
            {currentStreak > longestStreak.length ? (
              // Current streak is breaking the record!
              t('statistics.streakHistory.newRecord', { days: currentStreak })
            ) : currentStreak === longestStreak.length ? (
              // Current streak equals the record
              t('statistics.streakHistory.matchingRecord', { days: longestStreak.length })
            ) : (
              // Encourage to beat the record
              t('statistics.streakHistory.encouragement', { days: longestStreak.length })
            )}
          </p>
        </div>
      )}
    </div>
  );
}
