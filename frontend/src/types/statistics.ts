/**
 * TypeScript type definitions for Statistics API
 *
 * API responses use snake_case (from Django backend)
 * Frontend uses camelCase (React convention)
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
    [key: string]: number;
  };
  streak_history: {
    start_date: string;
    end_date: string;
    length: number;
  }[];
}

export interface StatisticsDataAPI {
  period: '7d' | '30d' | '90d' | '1y' | 'all';
  start_date: string;
  end_date: string;
  mood_analytics: MoodAnalyticsAPI;
  word_count_analytics: WordCountAnalyticsAPI;
  writing_patterns: WritingPatternsAPI;
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
    [key: string]: number;
  };
  streakHistory: {
    startDate: string;
    endDate: string;
    length: number;
  }[];
}

export interface StatisticsData {
  period: '7d' | '30d' | '90d' | '1y' | 'all';
  startDate: string;
  endDate: string;
  moodAnalytics: MoodAnalytics;
  wordCountAnalytics: WordCountAnalytics;
  writingPatterns: WritingPatterns;
}

// ============================================
// Helper Types
// ============================================

export type PeriodType = '7d' | '30d' | '90d' | '1y' | 'all';
