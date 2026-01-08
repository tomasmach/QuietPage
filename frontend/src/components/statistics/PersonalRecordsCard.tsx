/**
 * PersonalRecordsCard displays the user's personal writing records.
 *
 * Features:
 * - Longest entry (word count, date, title)
 * - Most productive day (word count, date, entry count)
 * - Longest streak (days)
 * - Longest goal streak (days, shown only if > 0)
 * - Brutalist styling with icons
 * - Encouraging empty state message
 */

import { Trophy, Medal, Award, Flame, Calendar } from 'lucide-react';
import type { PersonalRecords } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';

export interface PersonalRecordsCardProps {
  data: PersonalRecords | undefined;
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
 * Truncates a title if it's too long.
 */
function truncateTitle(title: string | null, maxLength: number = 30): string | null {
  if (!title) return null;
  if (title.length <= maxLength) return title;
  return `${title.substring(0, maxLength)}...`;
}

interface RecordRowProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  subtitle?: string;
}

/**
 * RecordRow displays a single record with icon, label, and value.
 */
function RecordRow({ icon, label, value, subtitle }: RecordRowProps) {
  return (
    <div className="flex items-start gap-4 py-4 border-b-2 border-dashed border-border last:border-b-0">
      <div className="p-3 border-2 border-border bg-bg-app shrink-0">
        {icon}
      </div>
      <div className="flex-1">
        <p className="text-[10px] font-bold uppercase tracking-widest text-text-muted font-mono mb-1">
          {label}
        </p>
        <p className="text-xl font-bold text-text-main font-mono leading-tight mb-1">
          {value}
        </p>
        {subtitle && (
          <p className="text-xs text-text-muted font-mono leading-relaxed">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}

export function PersonalRecordsCard({ data }: PersonalRecordsCardProps) {
  const { t, language } = useLanguage();

  // Check if there's any meaningful data
  const hasData =
    data &&
    (data.longestEntry || data.mostWordsInDay || data.longestStreak > 0 || data.longestGoalStreak > 0);

  // Empty state - no records yet
  if (!hasData) {
    return (
      <div className="border-2 border-border bg-bg-panel p-6 rounded-none shadow-hard h-fit">
        <div className="flex items-center gap-3 mb-4 pb-4 border-b-2 border-border">
          <div className="p-3 border-2 border-border bg-bg-app">
            <Trophy size={20} strokeWidth={2} className="text-text-muted" />
          </div>
          <h3 className="text-xs font-bold uppercase tracking-widest text-text-main font-mono">
            {t('statistics.records.title')}
          </h3>
        </div>
        <p className="text-sm font-mono text-text-muted">
          {t('statistics.records.noRecords')}
        </p>
      </div>
    );
  }

  const iconSize = 20;
  const iconStroke = 2;

  return (
    <div className="border-2 border-border bg-bg-panel p-6 rounded-none shadow-hard h-fit">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b-2 border-border">
        <div className="p-3 border-2 border-border bg-bg-app">
          <Trophy size={iconSize} strokeWidth={iconStroke} className="text-accent" />
        </div>
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-main font-mono">
          {t('statistics.records.title')}
        </h3>
      </div>

      {/* Records List */}
      <div className="space-y-0">
        {/* Longest Entry */}
        {data.longestEntry && (
          <RecordRow
            icon={<Award size={iconSize} strokeWidth={iconStroke} className="text-accent" />}
            label={t('statistics.records.longestEntry')}
            value={`${data.longestEntry.wordCount.toLocaleString(language === 'cs' ? 'cs-CZ' : 'en-US')} ${t('statistics.records.words')}`}
            subtitle={`${formatDate(data.longestEntry.date, language)}${data.longestEntry.title ? ` – ${truncateTitle(data.longestEntry.title)}` : ''}`}
          />
        )}

        {/* Most Productive Day */}
        {data.mostWordsInDay && (
          <RecordRow
            icon={<Medal size={iconSize} strokeWidth={iconStroke} className="text-accent" />}
            label={t('statistics.records.mostProductiveDay')}
            value={`${data.mostWordsInDay.wordCount.toLocaleString(language === 'cs' ? 'cs-CZ' : 'en-US')} ${t('statistics.records.words')}`}
            subtitle={`${formatDate(data.mostWordsInDay.date, language)} – ${data.mostWordsInDay.entryCount} ${t('statistics.records.entries')}`}
          />
        )}

        {/* Longest Streak */}
        {data.longestStreak > 0 && (
          <RecordRow
            icon={<Flame size={iconSize} strokeWidth={iconStroke} className="text-accent" />}
            label={t('statistics.records.longestStreak')}
            value={`${data.longestStreak} ${t('statistics.records.days')}`}
          />
        )}

        {/* Longest Goal Streak (only show if > 0) */}
        {data.longestGoalStreak > 0 && (
          <RecordRow
            icon={<Calendar size={iconSize} strokeWidth={iconStroke} className="text-accent" />}
            label={t('statistics.records.longestGoalStreak')}
            value={`${data.longestGoalStreak} ${t('statistics.records.days')}`}
          />
        )}
      </div>
    </div>
  );
}
