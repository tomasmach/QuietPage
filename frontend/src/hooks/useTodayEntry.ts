import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/api';
import type { EntryDetail } from './useEntry';

interface UseTodayEntryReturn {
  entry: EntryDetail | null;
  isLoading: boolean;
  error: Error | null;
  exists: boolean;
  refresh: () => Promise<void>;
}

/**
 * Hook pro fetchování dnešního daily note
 * Používá /api/v1/entries/today/
 */
export function useTodayEntry(): UseTodayEntryReturn {
  const [entry, setEntry] = useState<EntryDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [exists, setExists] = useState(false);

  const fetchTodayEntry = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get<EntryDetail>('/entries/today/');
      setEntry(response);
      setExists(true);
    } catch (err) {
      // 404 je očekáváno když dnes ještě není záznam
      if (err instanceof Error && err.message.includes('404')) {
        setEntry(null);
        setExists(false);
      } else {
        setError(err instanceof Error ? err : new Error('Failed to fetch today\'s entry'));
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTodayEntry();
  }, [fetchTodayEntry]);

  return {
    entry,
    isLoading,
    error,
    exists,
    refresh: fetchTodayEntry,
  };
}
