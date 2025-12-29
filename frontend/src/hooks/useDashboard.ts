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
      const response = await api.get<DashboardData>('/dashboard/');
      setData(response);
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
