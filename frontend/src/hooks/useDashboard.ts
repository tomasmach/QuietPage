import { useEffect, useState, useCallback } from 'react';
import { api } from '../lib/api';

export interface DashboardStats {
  todayWords: number;
  dailyGoal: number;
  currentStreak: number;
  longestStreak: number;
  totalEntries: number;
}

export interface RecentEntry {
  id: string;
  title: string;
  content_preview: string;
  created_at: string;
  mood_rating: number | null;
  word_count: number;
}

export interface Quote {
  text: string;
  author: string;
}

export interface FeaturedEntry {
  id: string;
  title: string;
  content_preview: string;
  created_at: string;
  word_count: number;
  days_ago: number;
}

export interface WeeklyStats {
  totalWords: number;
  bestDay: {
    date: string;
    words: number;
    weekday: string;
  } | null;
}

export interface DashboardData {
  greeting: string;
  stats: DashboardStats;
  recentEntries: RecentEntry[];
  quote: Quote | null;
  hasEntries: boolean;
  featuredEntry: FeaturedEntry | null;
  weeklyStats: WeeklyStats;
}

// API response with snake_case from backend
interface DashboardStatsAPI {
  today_words: number;
  daily_goal: number;
  current_streak: number;
  longest_streak: number;
  total_entries: number;
}

interface FeaturedEntryAPI {
  id: string;
  title: string;
  content_preview: string;
  created_at: string;
  word_count: number;
  days_ago: number;
}

interface WeeklyStatsAPI {
  total_words: number;
  best_day: {
    date: string;
    words: number;
    weekday: string;
  } | null;
}

interface DashboardDataAPI {
  greeting: string;
  stats: DashboardStatsAPI;
  recent_entries: RecentEntry[];
  quote: Quote | null;
  featured_entry: FeaturedEntryAPI | null;
  weekly_stats: WeeklyStatsAPI;
}

interface UseDashboardReturn {
  data: DashboardData | null;
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
  refreshFeaturedEntry: () => Promise<void>;
  isRefreshingFeatured: boolean;
}

/**
 * Hook for fetching dashboard data
 * Fetches from /api/v1/dashboard/
 */
export function useDashboard(): UseDashboardReturn {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isRefreshingFeatured, setIsRefreshingFeatured] = useState(false);

  const fetchDashboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get<DashboardDataAPI>('/dashboard/');

      // Convert snake_case from backend to camelCase for frontend
      const dashboardData: DashboardData = {
        greeting: response.greeting,
        stats: {
          todayWords: response.stats.today_words ?? 0,
          dailyGoal: response.stats.daily_goal ?? 750,
          currentStreak: response.stats.current_streak ?? 0,
          longestStreak: response.stats.longest_streak ?? 0,
          totalEntries: response.stats.total_entries ?? 0,
        },
        recentEntries: response.recent_entries || [],
        quote: response.quote,
        hasEntries: (response.recent_entries || []).length > 0,
        featuredEntry: response.featured_entry,
        weeklyStats: {
          totalWords: response.weekly_stats?.total_words ?? 0,
          bestDay: response.weekly_stats?.best_day ?? null,
        },
      };

      setData(dashboardData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch dashboard'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshFeaturedEntry = useCallback(async () => {
    if (!data) return;

    setIsRefreshingFeatured(true);

    try {
      const response = await api.post<{ featured_entry: FeaturedEntryAPI | null }>(
        '/dashboard/refresh-featured/'
      );

      setData(prev => prev ? {
        ...prev,
        featuredEntry: response.featured_entry,
      } : null);
    } catch (err) {
      console.error('Failed to refresh featured entry:', err);
    } finally {
      setIsRefreshingFeatured(false);
    }
  }, [data]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return {
    data,
    isLoading,
    error,
    refresh: fetchDashboard,
    refreshFeaturedEntry,
    isRefreshingFeatured,
  };
}
