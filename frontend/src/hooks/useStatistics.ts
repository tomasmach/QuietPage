import { useEffect, useState, useCallback } from 'react';
import { api } from '../lib/api';
import type {
  StatisticsData,
  StatisticsDataAPI,
  PeriodType,
} from '../types/statistics';

interface UseStatisticsReturn {
  data: StatisticsData | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

/**
 * Hook for fetching statistics data from the API.
 *
 * Fetches from /api/v1/statistics/?period={period}
 * Automatically refetches when period changes.
 *
 * @param period - Time period for statistics ('7d', '30d', '90d', '1y', 'all')
 * @returns Statistics data, loading state, error state, and refetch function
 *
 * @example
 * ```tsx
 * const { data, isLoading, error, refetch } = useStatistics('30d');
 * ```
 */
export function useStatistics(period: PeriodType = '30d'): UseStatisticsReturn {
  const [data, setData] = useState<StatisticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchStatistics = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get<StatisticsDataAPI>('/statistics/', { period });

      // Convert snake_case from backend to camelCase for frontend
      const statisticsData: StatisticsData = {
        period: response.period,
        startDate: response.start_date,
        endDate: response.end_date,
        moodAnalytics: {
          average: response.mood_analytics.average,
          distribution: response.mood_analytics.distribution,
          timeline: response.mood_analytics.timeline,
          totalRatedEntries: response.mood_analytics.total_rated_entries,
          trend: response.mood_analytics.trend,
        },
        wordCountAnalytics: {
          total: response.word_count_analytics.total,
          averagePerEntry: response.word_count_analytics.average_per_entry,
          averagePerDay: response.word_count_analytics.average_per_day,
          timeline: response.word_count_analytics.timeline.map(day => ({
            date: day.date,
            wordCount: day.word_count,
            entryCount: day.entry_count,
          })),
          totalEntries: response.word_count_analytics.total_entries,
          goalAchievementRate: response.word_count_analytics.goal_achievement_rate,
          bestDay: response.word_count_analytics.best_day ? {
            date: response.word_count_analytics.best_day.date,
            wordCount: response.word_count_analytics.best_day.word_count,
            entryCount: response.word_count_analytics.best_day.entry_count,
          } : null,
        },
        writingPatterns: {
          consistencyRate: response.writing_patterns.consistency_rate,
          timeOfDay: response.writing_patterns.time_of_day,
          dayOfWeek: response.writing_patterns.day_of_week,
          streakHistory: response.writing_patterns.streak_history.map(streak => ({
            startDate: streak.start_date,
            endDate: streak.end_date,
            length: streak.length,
          })),
        },
        tagAnalytics: {
          tags: response.tag_analytics.tags.map(tag => ({
            name: tag.name,
            entryCount: tag.entry_count,
            totalWords: tag.total_words,
            averageWords: tag.average_words,
            averageMood: tag.average_mood,
          })),
          totalTags: response.tag_analytics.total_tags,
        },
        milestones: {
          milestones: response.milestones.milestones.map(milestone => ({
            type: milestone.type,
            value: milestone.value,
            achieved: milestone.achieved,
            current: milestone.current,
          })),
        },
      };

      setData(statisticsData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch statistics'));
    } finally {
      setIsLoading(false);
    }
  }, [period]);

  useEffect(() => {
    fetchStatistics();
  }, [fetchStatistics]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchStatistics,
  };
}
