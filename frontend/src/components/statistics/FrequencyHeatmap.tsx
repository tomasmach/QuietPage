import { useState, useMemo } from 'react';
import type { WordCountAnalytics } from '../../types/statistics';
import { cn } from '../../lib/utils';
import { useLanguage } from '../../contexts/LanguageContext';

interface FrequencyHeatmapProps {
  data: WordCountAnalytics;
}

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

const DAYS_TO_SHOW = 90;
const DAYS_IN_WEEK = 7;

/**
 * Calculates dynamic intensity thresholds based on user's writing patterns.
 * Uses percentiles (33rd, 66th, 90th) of non-zero word counts.
 * Falls back to 750words.com standard if insufficient data.
 */
function calculateIntensityThresholds(timeline: WordCountAnalytics['timeline']): IntensityThresholds {
  // Get all non-zero word counts from the timeline
  const nonZeroCounts = timeline
    .map(day => day.wordCount)
    .filter(count => count > 0)
    .sort((a, b) => a - b);
  
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
 * Gets Tailwind classes for heatmap cell based on intensity
 */
function getIntensityClasses(intensity: number): string {
  const baseClasses = 'border border-border';
  
  switch (intensity) {
    case 0:
      return cn(baseClasses, 'bg-bg-panel'); // No writing - panel background
    case 1:
      return cn(baseClasses, 'bg-accent/20'); // Light - 20% opacity
    case 2:
      return cn(baseClasses, 'bg-accent/50'); // Medium - 50% opacity
    case 3:
      return cn(baseClasses, 'bg-accent'); // Dark - full accent
    default:
      return baseClasses;
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
 * Generates array of dates for the last 90 days, including padding.
 * Uses YYYY-MM-DD strings for date comparisons to avoid timezone issues.
 */
function generateDateArray(endDateStr: string): DayData[] {
  const days: DayData[] = [];
  const today = parseLocalDate(endDateStr);
  
  // Calculate start date (90 days ago)
  const startDate = new Date(today);
  startDate.setDate(startDate.getDate() - DAYS_TO_SHOW + 1);
  const startDateKey = toLocalDateString(startDate);
  const endDateKey = endDateStr;
  
  // Find the Sunday before start date (to align weeks)
  const firstDayOfWeek = startDate.getDay();
  const paddingDays = firstDayOfWeek; // Days to add before start
  
  const alignedStartDate = new Date(startDate);
  alignedStartDate.setDate(alignedStartDate.getDate() - paddingDays);
  
  // Generate all days from aligned start to today
  const currentDate = new Date(alignedStartDate);
  while (currentDate <= today) {
    const dateKey = toLocalDateString(currentDate);
    const isInPeriod = dateKey >= startDateKey && dateKey <= endDateKey;
    days.push({
      date: new Date(currentDate),
      dateKey,
      wordCount: 0,
      isInPeriod,
    });
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return days;
}

/**
 * Merges timeline data with date array.
 * Uses dateKey (YYYY-MM-DD string) for comparisons to avoid timezone issues.
 */
function mergeDayData(days: DayData[], timeline: WordCountAnalytics['timeline']): DayData[] {
  const timelineMap = new Map<string, number>();
  
  // Build map of date -> total word count
  // API returns dates as YYYY-MM-DD strings, use directly
  timeline.forEach(({ date, wordCount }) => {
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

export function FrequencyHeatmap({ data }: FrequencyHeatmapProps) {
  const { t, language } = useLanguage();
  const [hoveredDay, setHoveredDay] = useState<DayData | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  
  // Calculate dynamic intensity thresholds based on user's writing patterns
  const intensityThresholds = useMemo(
    () => calculateIntensityThresholds(data.timeline),
    [data.timeline]
  );
  
  // Generate date array and merge with timeline data
  // Use the date string directly from API (YYYY-MM-DD format) to avoid timezone issues
  const endDateStr = data.timeline.length > 0 
    ? data.timeline[data.timeline.length - 1].date
    : toLocalDateString(new Date());
  
  // Get locale code for date formatting
  const localeCode = language === 'cs' ? 'cs-CZ' : 'en-US';

  const days = generateDateArray(endDateStr);
  const mergedDays = mergeDayData(days, data.timeline);
  const weeks = groupIntoWeeks(mergedDays);
  const monthLabels = getMonthLabels(weeks, localeCode);
  
  const handleMouseEnter = (day: DayData, event: React.MouseEvent<HTMLDivElement>) => {
    if (!day.isInPeriod) return;
    
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
  
  return (
    <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
        {t('statistics.frequencyHeatmap.title')}
      </h3>
      
      <div className="relative">
        {/* Month labels */}
        <div className="flex ml-6 mb-2">
          <div className="grid gap-[2px] sm:gap-1" style={{ gridTemplateColumns: `repeat(${weeks.length}, 12px)` }}>
            {weeks.map((_, weekIndex) => {
              const monthLabel = monthLabels.find(m => m.weekIndex === weekIndex);
              return (
                <div key={weekIndex} className="h-4 flex items-center justify-start">
                  {monthLabel && (
                    <span className="text-[8px] sm:text-[10px] font-mono text-text-muted whitespace-nowrap">
                      {monthLabel.label}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Heatmap grid */}
        <div className="flex">
          {/* Day of week labels */}
          <div className="flex flex-col gap-[2px] sm:gap-1 mr-2">
            {[0, 1, 2, 3, 4, 5, 6].map(dayIndex => (
              <div
                key={dayIndex}
                className="w-4 h-[8px] sm:h-3 flex items-center justify-end"
              >
                <span className="text-[8px] sm:text-[10px] font-mono text-text-muted">
                  {getDayOfWeekLabel(dayIndex)}
                </span>
              </div>
            ))}
          </div>
          
          {/* Calendar grid */}
          <div className="grid gap-[2px] sm:gap-1" style={{ gridTemplateColumns: `repeat(${weeks.length}, 8px)`, gridAutoRows: '8px' }}>
            {weeks.map((week, weekIndex) =>
              week.map((day, dayIndex) => {
                const intensity = day.isInPeriod ? getIntensityLevel(day.wordCount, intensityThresholds) : 0;
                return (
                  <div
                    key={`${weekIndex}-${dayIndex}`}
                    className={cn(
                      'w-[8px] h-[8px] sm:w-3 sm:h-3 rounded-none transition-all duration-150 cursor-pointer',
                      getIntensityClasses(intensity),
                      day.isInPeriod && 'hover:ring-1 hover:ring-accent hover:scale-110'
                    )}
                    onMouseEnter={(e) => handleMouseEnter(day, e)}
                    onMouseLeave={handleMouseLeave}
                    style={{ opacity: day.isInPeriod ? 1 : 0.3 }}
                  />
                );
              })
            )}
          </div>
        </div>
        
        {/* Legend */}
        <div className="flex items-center justify-end gap-2 mt-4 text-[10px] font-mono text-text-muted">
          <span>{t('statistics.frequencyHeatmap.less')}</span>
          <div className="flex gap-1">
            {[0, 1, 2, 3].map(level => (
              <div
                key={level}
                className={cn('w-3 h-3 border border-border', getIntensityClasses(level))}
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
