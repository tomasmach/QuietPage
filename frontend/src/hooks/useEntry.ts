import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/api';

export interface EntryDetail {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  mood_rating: number | null;
  word_count: number;
  tags: string[];
}

export interface EntryFormData {
  title?: string;
  content: string;
  mood_rating?: number | null;
  tags?: string[];
}

interface UseEntryReturn {
  entry: EntryDetail | null;
  isLoading: boolean;
  error: Error | null;
  save: (data: EntryFormData) => Promise<EntryDetail>;
  remove: () => Promise<void>;
  refresh: () => Promise<void>;
}

/**
 * Hook for managing a single entry
 * Fetches from /api/v1/entries/{id}/
 * Supports create, update, and delete operations
 */
export function useEntry(id?: string): UseEntryReturn {
  const [entry, setEntry] = useState<EntryDetail | null>(null);
  const [isLoading, setIsLoading] = useState(!!id);
  const [error, setError] = useState<Error | null>(null);

  const fetchEntry = useCallback(async () => {
    if (!id) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get<EntryDetail>(`/entries/${id}/`);
      setEntry(response);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch entry'));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      fetchEntry();
    }
  }, [id, fetchEntry]);

  /**
   * Save entry (create or update)
   */
  const save = async (data: EntryFormData): Promise<EntryDetail> => {
    setError(null);

    try {
      let response: EntryDetail;

      if (id) {
        // Update existing entry
        response = await api.patch<EntryDetail>(`/entries/${id}/`, data);
      } else {
        // Create new entry
        response = await api.post<EntryDetail>('/entries/', data);
      }

      setEntry(response);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to save entry');
      setError(error);
      throw error;
    }
  };

  /**
   * Delete entry
   */
  const remove = async (): Promise<void> => {
    if (!id) {
      throw new Error('Cannot delete entry without ID');
    }

    setError(null);

    try {
      await api.delete(`/entries/${id}/`);
      setEntry(null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete entry');
      setError(error);
      throw error;
    }
  };

  return {
    entry,
    isLoading,
    error,
    save,
    remove,
    refresh: fetchEntry,
  };
}
