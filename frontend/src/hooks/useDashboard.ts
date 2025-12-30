import { useEffect, useState } from 'react';
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

export interface DashboardData {
  greeting: string;
  stats: DashboardStats;
  recentEntries: RecentEntry[];
  quote: Quote | null;
  hasEntries: boolean;
}

interface UseDashboardReturn {
  data: DashboardData | null;
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
}

/**
 * Hook for fetching dashboard data
 * Fetches from /api/v1/dashboard/
 */
export function useDashboard(): UseDashboardReturn {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchDashboard = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get<any>('/dashboard/');

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
      };

      setData(dashboardData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch dashboard'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  return {
    data,
    isLoading,
    error,
    refresh: fetchDashboard,
  };
}
