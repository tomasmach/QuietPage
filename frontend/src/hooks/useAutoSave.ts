import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../lib/api';
import type { EntryFormData } from './useEntry';

interface AutoSaveOptions {
  debounceMs?: number;
  onSuccess?: (id: string) => void;
  onError?: (error: Error) => void;
}

interface UseAutoSaveReturn {
  save: (data: EntryFormData) => void;
  isSaving: boolean;
  lastSaved: Date | null;
  error: Error | null;
}

/**
 * Hook for auto-saving entries with debouncing
 * Posts to /api/v1/entries/autosave/
 */
export function useAutoSave(
  entryId?: string,
  options: AutoSaveOptions = {}
): UseAutoSaveReturn {
  const { debounceMs = 1000, onSuccess, onError } = options;

  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const debounceTimerRef = useRef<number | null>(null);
  const saveQueueRef = useRef<EntryFormData | null>(null);

  /**
   * Perform the actual save operation
   */
  const performSave = useCallback(async (data: EntryFormData) => {
    setIsSaving(true);
    setError(null);

    try {
      const payload = entryId ? { ...data, id: entryId } : data;
      const response = await api.post<{ id: string }>('/entries/autosave/', payload);

      setLastSaved(new Date());

      if (onSuccess && response.id) {
        onSuccess(response.id);
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Auto-save failed');
      setError(error);

      if (onError) {
        onError(error);
      }
    } finally {
      setIsSaving(false);
    }
  }, [entryId, onSuccess, onError]);

  /**
   * Debounced save function
   */
  const save = useCallback((data: EntryFormData) => {
    // Store the latest data
    saveQueueRef.current = data;

    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Set new timer
    debounceTimerRef.current = setTimeout(() => {
      if (saveQueueRef.current) {
        performSave(saveQueueRef.current);
        saveQueueRef.current = null;
      }
    }, debounceMs);
  }, [debounceMs, performSave]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  return {
    save,
    isSaving,
    lastSaved,
    error,
  };
}
