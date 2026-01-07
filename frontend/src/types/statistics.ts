/**
 * TypeScript type definitions for Statistics API
 *
 * API responses use snake_case (from Django backend)
 * Frontend uses camelCase (React convention)
 * 
 * Design System - Color Guidelines (per styles.md):
 * 
 * Core Principle: Use CSS variables for theme-aware colors
 * - Primary: var(--color-accent) - Main interactive/emphasis color
 * - Muted: var(--color-text-muted) - Secondary/de-emphasized elements
 * - Borders: var(--color-border) - All borders (always 2px solid)
 * - Background: var(--color-bg-panel) - Cards/widgets
 * - Shadows: shadow-hard (4px 4px 0px 0px var(--color-shadow))
 * - Text: var(--color-text-main) for primary, var(--color-text-muted) for secondary
 * 
 * Chart Color Recommendations:
 * - Consistency Rate: var(--color-accent) with progress bar styling
 * - Time of Day: Semantic colors (amber/orange/purple/blue) - exception for time representation
 * - Day of Week: var(--color-accent) for highlighted bars, var(--color-text-muted) for others
 * - Streak History: var(--color-accent) for emphasis, borders and backgrounds per design system
 * 
 * Typography:
 * - Font: IBM Plex Mono (monospace) for ALL text
 * - Headers: uppercase, bold, tracking-widest
 * - Use hard shadows (shadow-hard), sharp borders (rounded-none), 2px borders
 */

// ============================================
// API Response Types (snake_case from backend)
// ============================================

export interface MoodAnalyticsAPI {
  average: number | null;
  distribution: {
    "1": number;
    "2": number;
    "3": number;
    "4": number;
    "5": number;
  };
  timeline: {
    date: string;
    average: number | null;
    count: number;
  }[];
  total_rated_entries: number;
  trend: 'improving' | 'declining' | 'stable';
}

export interface WordCountAnalyticsAPI {
  total: number;
  average_per_entry: number;
  average_per_day: number;
  timeline: {
    date: string;
    word_count: number;
    entry_count: number;
  }[];
  total_entries: number;
  goal_achievement_rate: number;
  best_day: {
    date: string;
    word_count: number;
    entry_count: number;
  } | null;
}

export interface WritingPatternsAPI {
  consistency_rate: number;
  time_of_day: {
    morning: number;
    afternoon: number;
    evening: number;
    night: number;
  };
  day_of_week: {
    monday: number;
    tuesday: number;
    wednesday: number;
    thursday: number;
    friday: number;
    saturday: number;
    sunday: number;
  };
  streak_history: {
    start_date: string;
    end_date: string;
    length: number;
  }[];
}

export interface TagDataAPI {
  name: string;
  entry_count: number;
  total_words: number;
  average_words: number;
  average_mood: number | null;
}

export interface TagAnalyticsAPI {
  tags: TagDataAPI[];
  total_tags: number;
}

export type MilestoneType = 'entries' | 'words' | 'streak';

export interface MilestoneAPI {
  type: MilestoneType;
  value: number;
  achieved: boolean;
  current: number;
}

export interface MilestonesAPI {
  milestones: MilestoneAPI[];
}

export interface GoalStreakAPI {
  current: number;
  longest: number;
  goal: number;
}

export interface LongestEntryAPI {
  date: string;
  word_count: number;
  title: string | null;
  entry_id: string;
}

export interface MostWordsInDayAPI {
  date: string;
  word_count: number;
  entry_count: number;
}

export interface PersonalRecordsAPI {
  longest_entry: LongestEntryAPI | null;
  most_words_in_day: MostWordsInDayAPI | null;
  longest_streak: number;
  longest_goal_streak: number;
}

export interface StatisticsDataAPI {
  period: '7d' | '30d' | '90d' | '1y' | 'all';
  start_date: string;
  end_date: string;
  mood_analytics: MoodAnalyticsAPI;
  word_count_analytics: WordCountAnalyticsAPI;
  writing_patterns: WritingPatternsAPI;
  tag_analytics: TagAnalyticsAPI;
  milestones: MilestonesAPI;
  goal_streak: GoalStreakAPI;
  personal_records: PersonalRecordsAPI;
}

// ============================================
// Frontend Types (camelCase)
// ============================================

export interface MoodAnalytics {
  average: number | null;
  distribution: {
    "1": number;
    "2": number;
    "3": number;
    "4": number;
    "5": number;
  };
  timeline: {
    date: string;
    average: number | null;
    count: number;
  }[];
  totalRatedEntries: number;
  trend: 'improving' | 'declining' | 'stable';
}

export interface WordCountAnalytics {
  total: number;
  averagePerEntry: number;
  averagePerDay: number;
  timeline: {
    date: string;
    wordCount: number;
    entryCount: number;
  }[];
  totalEntries: number;
  goalAchievementRate: number;
  bestDay: {
    date: string;
    wordCount: number;
    entryCount: number;
  } | null;
}

export interface WritingPatterns {
  consistencyRate: number;
  timeOfDay: {
    morning: number;
    afternoon: number;
    evening: number;
    night: number;
  };
  dayOfWeek: {
    monday: number;
    tuesday: number;
    wednesday: number;
    thursday: number;
    friday: number;
    saturday: number;
    sunday: number;
    [key: string]: number; // Allow string indexing for dynamic access
  };
  streakHistory: {
    startDate: string;
    endDate: string;
    length: number;
  }[];
}

export interface TagData {
  name: string;
  entryCount: number;
  totalWords: number;
  averageWords: number;
  averageMood: number | null;
}

export interface TagAnalytics {
  tags: TagData[];
  totalTags: number;
}

export interface Milestone {
  type: MilestoneType;
  value: number;
  achieved: boolean;
  current: number;
}

export interface Milestones {
  milestones: Milestone[];
}

export interface GoalStreak {
  current: number;
  longest: number;
  goal: number;
}

export interface LongestEntry {
  date: string;
  wordCount: number;
  title: string | null;
  entryId: string;
}

export interface MostWordsInDay {
  date: string;
  wordCount: number;
  entryCount: number;
}

export interface PersonalRecords {
  longestEntry: LongestEntry | null;
  mostWordsInDay: MostWordsInDay | null;
  longestStreak: number;
  longestGoalStreak: number;
}

export interface StatisticsData {
  period: '7d' | '30d' | '90d' | '1y' | 'all';
  startDate: string;
  endDate: string;
  moodAnalytics: MoodAnalytics;
  wordCountAnalytics: WordCountAnalytics;
  writingPatterns: WritingPatterns;
  tagAnalytics: TagAnalytics;
  milestones: Milestones;
  goalStreak: GoalStreak;
  personalRecords: PersonalRecords;
}

// ============================================
// Helper Types
// ============================================

export type PeriodType = '7d' | '30d' | '90d' | '1y' | 'all';
