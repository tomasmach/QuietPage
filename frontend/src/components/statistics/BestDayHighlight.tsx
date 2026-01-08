/**
 * BestDayHighlight component celebrates the user's best writing day.
 * 
 * Features:
 * - Highlighted card showing the best writing day achievement
 * - Displays formatted date, word count, and entry count
 * - Trophy icon for celebratory feel
 * - Brutalist styling with accent treatment
 * - Encouraging empty state message
 */

import { Trophy, Pencil } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

export interface BestDayData {
  date: string;
  wordCount: number;
  entryCount: number;
}

export interface BestDayHighlightProps {
  data: BestDayData | undefined;
}

/**
 * Formats a date string to localized format (e.g., "Dec 1, 2025")
 * Parses ISO date string (YYYY-MM-DD) as local date to avoid timezone shifts.
 */
function formatDate(dateString: string, language: 'cs' | 'en'): string {
  // Parse ISO date string (YYYY-MM-DD) into components
  const parts = dateString.split(/-/);
  
  // Guard against invalid input
  if (parts.length !== 3) {
    return dateString; // Return original string if parsing fails
  }
  
  const year = Number(parts[0]);
  const monthIndex = Number(parts[1]) - 1; // Month is 0-indexed
  const day = Number(parts[2]);
  
  // Validate parsed values
  if (isNaN(year) || isNaN(monthIndex) || isNaN(day)) {
    return dateString; // Return original string if parsing fails
  }
  
  // Construct local Date (no timezone shift)
  const date = new Date(year, monthIndex, day);
  
  const options: Intl.DateTimeFormatOptions = {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  };
  
  return date.toLocaleDateString(language === 'cs' ? 'cs-CZ' : 'en-US', options);
}

export function BestDayHighlight({ data }: BestDayHighlightProps) {
  const { t, language } = useLanguage();

  // Empty state - no best day data yet
  if (!data) {
    return (
      <div className="border-2 border-border bg-bg-panel p-6 rounded-none shadow-hard">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 border-2 border-border bg-bg-app">
            <Pencil size={20} strokeWidth={2} className="text-text-muted" />
          </div>
          <h3 className="text-xs font-bold uppercase tracking-widest text-text-main font-mono">
            {t('statistics.bestDay.title')}
          </h3>
        </div>
        <p className="text-sm font-mono text-text-muted">
          {t('statistics.bestDay.noData')}
        </p>
      </div>
    );
  }

  return (
    <div className="border-2 border-accent-fg bg-accent text-accent-fg p-6 rounded-none shadow-hard relative overflow-hidden">
      {/* Decorative background pattern */}
      <div className="absolute top-1/2 right-4 -translate-y-2/3 opacity-10 pointer-events-none">
        <Trophy size={100} strokeWidth={1} />
      </div>
      
      {/* Header with Trophy */}
      <div className="flex items-center gap-3 mb-4 relative">
        <div className="p-2 border-2 border-current bg-accent-fg/10">
          <Trophy size={20} strokeWidth={2} />
        </div>
        <h3 className="text-xs font-bold uppercase tracking-widest font-mono">
          {t('statistics.bestDay.title')}
        </h3>
      </div>
      
      {/* Date */}
      <p className="text-lg font-bold font-mono mb-4 relative capitalize">
        {formatDate(data.date, language)}
      </p>
      
      {/* Stats */}
      <div className="flex gap-6 relative">
        {/* Word Count */}
        <div>
          <p className="text-3xl font-bold font-mono">
            {data.wordCount.toLocaleString(language === 'cs' ? 'cs-CZ' : 'en-US')}
          </p>
          <p className="text-xs font-mono opacity-80 uppercase tracking-wider">
            {t('statistics.bestDay.words')}
          </p>
        </div>
        
        {/* Entry Count */}
        <div className="border-l-2 border-current pl-6 opacity-80">
          <p className="text-3xl font-bold font-mono">
            {data.entryCount.toLocaleString(language === 'cs' ? 'cs-CZ' : 'en-US')}
          </p>
          <p className="text-xs font-mono opacity-80 uppercase tracking-wider">
            {t('statistics.bestDay.entries')}
          </p>
        </div>
      </div>
    </div>
  );
}
