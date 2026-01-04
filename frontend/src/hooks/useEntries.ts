import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/api';

export interface Entry {
  id: string;
  title: string;
  content_preview?: string;
  created_at: string;
  updated_at: string;
  mood_rating: number | null;
  word_count: number;
  tags: string[];
}

interface EntriesResponse {
  results: Entry[];
  count: number;
  next: string | null;
  previous: string | null;
}

interface UseEntriesReturn {
  entries: Entry[];
  isLoading: boolean;
  error: Error | null;
  page: number;
  setPage: (page: number) => void;
  hasMore: boolean;
  totalCount: number;
  refresh: () => Promise<void>;
}

/**
 * Hook for fetching paginated entries list
 * Fetches from /api/v1/entries/
 */
export function useEntries(pageSize = 20): UseEntriesReturn {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const fetchEntries = useCallback(async (pageNum: number) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get<EntriesResponse>('/entries/', {
        page: pageNum,
        page_size: pageSize,
      });

      setEntries(response.results);
      setTotalCount(response.count);
      setHasMore(response.next !== null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch entries'));
    } finally {
      setIsLoading(false);
    }
  }, [pageSize]);

  useEffect(() => {
    fetchEntries(page);
  }, [page, fetchEntries]);

  return {
    entries,
    isLoading,
    error,
    page,
    setPage,
    hasMore,
    totalCount,
    refresh: () => fetchEntries(page),
  };
}
