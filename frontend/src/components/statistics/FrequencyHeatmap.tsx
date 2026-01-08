import { useState, useMemo, useEffect } from 'react';
import { cn } from '../../lib/utils';
import { useLanguage } from '../../contexts/LanguageContext';
import { api } from '../../lib/api';

interface DayData {
  date: Date;
  dateKey: string; // YYYY-MM-DD format for consistent comparisons
  wordCount: number;
  isInPeriod: boolean;
}

interface IntensityThresholds {
  low: number;    // Threshold for level 1
  medium: number; // Threshold for level 2
  high: number;   // Threshold for level 3
}

type TimelineData = Array<{
  date: string;
  wordCount: number;
  entryCount: number;
}>;

const DAYS_IN_WEEK = 7;

/**
 * Calculates dynamic intensity thresholds based on user's writing patterns.
 * Uses percentiles (33rd, 66th, 90th) of non-zero word counts.
 * Falls back to 750words.com standard if insufficient data.
 */
function calculateIntensityThresholds(timeline: TimelineData): IntensityThresholds {
  // Get all non-zero word counts from the timeline
  const nonZeroCounts = timeline
    .map((day: { wordCount: number }) => day.wordCount)
    .filter((count: number) => count > 0)
    .sort((a: number, b: number) => a - b);
  
  // If we have less than 10 days of data, use fixed 750words.com thresholds
  if (nonZeroCounts.length < 10) {
    return {
      low: 250,    // Any writing
      medium: 750, // Goal achieved
      high: 1500,  // Exceeded goal
    };
  }
  
  // Calculate percentiles for dynamic thresholds
  const getPercentile = (arr: number[], percentile: number): number => {
    const index = Math.ceil((percentile / 100) * arr.length) - 1;
    return arr[Math.max(0, index)];
  };
  
  return {
    low: getPercentile(nonZeroCounts, 33),    // 33rd percentile
    medium: getPercentile(nonZeroCounts, 66), // 66th percentile (median-ish)
    high: getPercentile(nonZeroCounts, 90),   // 90th percentile (best days)
  };
}

/**
 * Gets the intensity level based on word count and dynamic thresholds
 * - 0: No writing (gray)
 * - 1: Below 33rd percentile (light accent)
 * - 2: Between 33rd-66th percentile (medium accent)
 * - 3: Above 66th percentile (dark accent)
 */
function getIntensityLevel(wordCount: number, thresholds: IntensityThresholds): number {
  if (wordCount === 0) return 0;
  if (wordCount < thresholds.low) return 1;
  if (wordCount < thresholds.medium) return 2;
  if (wordCount < thresholds.high) return 3;
  return 3; // Best performance
}

/**
 * Gets inline styles for heatmap cell based on intensity.
 * Uses the same gradient as TimeOfDayChart (--color-chart-1 through --color-chart-4)
 */
function getIntensityStyles(intensity: number): { backgroundColor: string } {
  switch (intensity) {
    case 0:
      return { backgroundColor: 'var(--color-bg-panel)' }; // No writing - panel background
    case 1:
      return { backgroundColor: 'var(--color-chart-4)' }; // Lightest
    case 2:
      return { backgroundColor: 'var(--color-chart-3)' }; // Medium
    case 3:
      return { backgroundColor: 'var(--color-chart-1)' }; // Darkest (highest intensity)
    default:
      return { backgroundColor: 'var(--color-bg-panel)' };
  }
}

/**
 * Formats word count for display in tooltip
 */
function formatWordCount(count: number, t: (key: string) => string): string {
  if (count === 0) return t('statistics.frequencyHeatmap.noWriting');
  return `${count.toLocaleString()} ${t('statistics.frequencyHeatmap.words')}`;
}

/**
 * Formats date for tooltip
 */
function formatDate(date: Date, locale: string): string {
  return date.toLocaleDateString(locale, {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Gets day of week label (0 = Sunday, 6 = Saturday)
 */
function getDayOfWeekLabel(dayIndex: number): string {
  const labels = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
  return labels[dayIndex];
}

/**
 * Groups days into weeks (7 days each) for grid layout
 */
function groupIntoWeeks(days: DayData[]): DayData[][] {
  const weeks: DayData[][] = [];
  
  for (let i = 0; i < days.length; i += DAYS_IN_WEEK) {
    weeks.push(days.slice(i, i + DAYS_IN_WEEK));
  }
  
  return weeks;
}

/**
 * Formats a Date to YYYY-MM-DD string in local time (not UTC).
 * This avoids timezone issues when comparing dates.
 */
function toLocalDateString(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Parses a YYYY-MM-DD string to a Date in local time.
 * Using string parsing avoids timezone offset issues that occur with new Date(isoString).
 */
function parseLocalDate(dateString: string): Date {
  const [year, month, day] = dateString.split('-').map(Number);
  return new Date(year, month - 1, day);
}

/**
 * Generates array of dates for the specified period.
 * GitHub-style: starts from first Sunday before period, ends on actual end date.
 * Uses YYYY-MM-DD strings for date comparisons to avoid timezone issues.
 * All visible days will show data (including padding days before the period).
 */
function generateDateArray(endDateStr: string, daysToShow: number): DayData[] {
  const days: DayData[] = [];
  const today = parseLocalDate(endDateStr);
  
  // Calculate start date (N days ago)
  const startDate = new Date(today);
  startDate.setDate(startDate.getDate() - daysToShow + 1);
  
  // Find the Sunday before or on start date (to align weeks)
  const firstDayOfWeek = startDate.getDay();
  const alignedStartDate = new Date(startDate);
  alignedStartDate.setDate(alignedStartDate.getDate() - firstDayOfWeek);
  
  // Generate all days from aligned start to today
  // All days are "in period" for data purposes (no greyed out days)
  const currentDate = new Date(alignedStartDate);
  while (currentDate <= today) {
    const dateKey = toLocalDateString(currentDate);
    days.push({
      date: new Date(currentDate),
      dateKey,
      wordCount: 0,
      isInPeriod: true, // All visible days show data
    });
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return days;
}

/**
 * Merges timeline data with date array.
 * Uses dateKey (YYYY-MM-DD string) for comparisons to avoid timezone issues.
 */
function mergeDayData(days: DayData[], timeline: TimelineData): DayData[] {
  const timelineMap = new Map<string, number>();
  
  // Build map of date -> total word count
  // API returns dates as YYYY-MM-DD strings, use directly
  timeline.forEach(({ date, wordCount }: { date: string; wordCount: number }) => {
    timelineMap.set(date, (timelineMap.get(date) || 0) + wordCount);
  });
  
  // Merge with generated days using dateKey for consistent comparison
  return days.map(day => {
    const wordCount = timelineMap.get(day.dateKey) || 0;
    return { ...day, wordCount };
  });
}

/**
 * Gets month labels for heatmap columns
 */
function getMonthLabels(weeks: DayData[][], localeCode: string): { weekIndex: number; label: string }[] {
  const labels: { weekIndex: number; label: string }[] = [];
  let lastMonth = -1;
  
  weeks.forEach((week, weekIndex) => {
    if (week.length === 0) return;
    
    const firstDayOfWeek = week[0];
    if (!firstDayOfWeek.isInPeriod) return;
    
    const month = firstDayOfWeek.date.getMonth();
    
    // Add label if it's the first week or if month changed
    if (month !== lastMonth) {
      labels.push({
        weekIndex,
        label: firstDayOfWeek.date.toLocaleDateString(localeCode, { month: 'short' }).toUpperCase(),
      });
      lastMonth = month;
    }
  });
  
  return labels;
}

export function FrequencyHeatmap() {
  const { t, language } = useLanguage();
  const [hoveredDay, setHoveredDay] = useState<DayData | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [yearData, setYearData] = useState<TimelineData>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<Error | null>(null);
  
  // Fixed to show last year (365 days) - always, regardless of selected period
  const daysToShow = 365;
  
  // Fetch year data separately (always 1y period for heatmap)
  useEffect(() => {
    const fetchYearData = async () => {
      setIsLoading(true);
      try {
        const response = await api.get<{ word_count_analytics: { timeline: { date: string; word_count: number; entry_count: number }[] } }>('/statistics/', { period: '1y' });
        setFetchError(null); // Clear error on successful fetch
        setYearData(response.word_count_analytics.timeline.map(day => ({
          date: day.date,
          wordCount: day.word_count,
          entryCount: day.entry_count,
        })));
      } catch (error) {
        console.error('Failed to fetch year data for heatmap:', error);
        setFetchError(error instanceof Error ? error : new Error('Failed to fetch data'));
        setYearData([]);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchYearData();
  }, []); // Only fetch once on mount
  
  // Calculate dynamic intensity thresholds based on year data
  const intensityThresholds = useMemo(
    () => calculateIntensityThresholds(yearData),
    [yearData]
  );
  
  // Generate date array for the last 365 days from today
  // Always use today's date, not the end of the data timeline
  const endDateStr = toLocalDateString(new Date());
  
  // Get locale code for date formatting
  const localeCode = language === 'cs' ? 'cs-CZ' : 'en-US';

  const days = generateDateArray(endDateStr, daysToShow);
  const mergedDays = mergeDayData(days, yearData);
  const weeks = groupIntoWeeks(mergedDays);
  const monthLabels = getMonthLabels(weeks, localeCode);
  
  const handleMouseEnter = (day: DayData, event: React.MouseEvent<HTMLDivElement>) => {
    setHoveredDay(day);
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 8,
    });
  };
  
  const handleMouseLeave = () => {
    setHoveredDay(null);
  };
  
  if (isLoading) {
    return (
      <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
          {t('statistics.frequencyHeatmap.title')} (LAST YEAR)
        </h3>
        <div className="flex items-center justify-center h-32">
          <span className="text-text-muted font-mono text-sm">Loading...</span>
        </div>
      </div>
    );
  }
  
  if (fetchError) {
    return (
      <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
          {t('statistics.frequencyHeatmap.title')} (LAST YEAR)
        </h3>
        <div className="flex items-center justify-center h-32">
          <div className="text-center">
            <p className="text-text-muted font-mono text-sm mb-2">
              {t('statistics.frequencyHeatmap.loadError')}
            </p>
            <p className="text-text-muted font-mono text-xs opacity-70">
              {fetchError.message}
            </p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
        {t('statistics.frequencyHeatmap.title')} (LAST YEAR)
      </h3>
      
      <div className="relative">
        {/* Month labels */}
        <div className="flex ml-4 mb-1 overflow-hidden">
          <div className="grid gap-[1px] flex-1" style={{ gridTemplateColumns: `repeat(${weeks.length}, minmax(0, 1fr))` }}>
            {weeks.map((_, weekIndex) => {
              const monthLabel = monthLabels.find(m => m.weekIndex === weekIndex);
              return (
                <div key={weekIndex} className="h-3 flex items-center justify-start overflow-hidden">
                  {monthLabel && (
                    <span className="text-[8px] font-mono text-text-muted whitespace-nowrap">
                      {monthLabel.label}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Heatmap grid */}
        <div className="flex overflow-hidden">
          {/* Day of week labels */}
          <div className="flex flex-col gap-[1px] mr-1">
            {[0, 1, 2, 3, 4, 5, 6].map(dayIndex => (
              <div
                key={dayIndex}
                className="w-3 flex items-center justify-end"
                style={{ aspectRatio: '1' }}
              >
                <span className="text-[8px] font-mono text-text-muted">
                  {getDayOfWeekLabel(dayIndex)}
                </span>
              </div>
            ))}
          </div>
          
          {/* Calendar grid - days go vertically (top to bottom), weeks horizontally (left to right) */}
          <div className="grid gap-[1px] flex-1 overflow-hidden" style={{ gridTemplateColumns: `repeat(${weeks.length}, minmax(0, 1fr))`, gridTemplateRows: 'repeat(7, minmax(0, 1fr))' }}>
            {mergedDays.map((day, index) => {
              const weekIndex = Math.floor(index / 7);
              const dayOfWeek = index % 7;
              const intensity = getIntensityLevel(day.wordCount, intensityThresholds);
              const intensityStyles = getIntensityStyles(intensity);
              return (
                <div
                  key={`${day.dateKey}`}
                  className={cn(
                    'rounded-none transition-all duration-150 cursor-pointer min-w-0 min-h-0 border border-border',
                    'hover:ring-1 hover:ring-accent'
                  )}
                  onMouseEnter={(e) => handleMouseEnter(day, e)}
                  onMouseLeave={handleMouseLeave}
                  style={{ 
                    aspectRatio: '1',
                    gridColumn: weekIndex + 1,
                    gridRow: dayOfWeek + 1,
                    ...intensityStyles
                  }}
                />
              );
            })}
          </div>
        </div>
        
        {/* Legend */}
        <div className="flex items-center justify-end gap-2 mt-3 text-[9px] font-mono text-text-muted">
          <span>{t('statistics.frequencyHeatmap.less')}</span>
          <div className="flex gap-[2px]">
            {[0, 1, 2, 3].map(level => (
              <div
                key={level}
                className="w-2.5 h-2.5 border border-border"
                style={getIntensityStyles(level)}
              />
            ))}
          </div>
          <span>{t('statistics.frequencyHeatmap.more')}</span>
        </div>
        
        {/* Tooltip */}
        {hoveredDay && (
          <div
            className="fixed z-50 pointer-events-none"
            style={{
              left: `${tooltipPosition.x}px`,
              top: `${tooltipPosition.y}px`,
              transform: 'translate(-50%, -100%)',
            }}
          >
            <div className="bg-bg-panel border-2 border-border px-3 py-2 shadow-hard">
              <p className="text-xs font-mono text-text-main whitespace-nowrap">
                {formatDate(hoveredDay.date, localeCode)}
              </p>
              <p className="text-xs font-mono text-text-muted whitespace-nowrap">
                {formatWordCount(hoveredDay.wordCount, t)}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
