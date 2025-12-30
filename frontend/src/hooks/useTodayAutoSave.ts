import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../lib/api';
import type { EntryFormData, EntryDetail } from './useEntry';

interface TodayAutoSaveOptions {
  debounceMs?: number;
  onSuccess?: (entry: EntryDetail) => void;
  onError?: (error: Error) => void;
}

interface UseTodayAutoSaveReturn {
  save: (data: EntryFormData) => void;
  isSaving: boolean;
  lastSaved: Date | null;
  error: Error | null;
}

/**
 * Hook pro autosave dnešního daily note
 * Postuje na /api/v1/entries/today/
 *
 * KRITICKÉ: Ukládá jen když content není prázdný
 */
export function useTodayAutoSave(
  options: TodayAutoSaveOptions = {}
): UseTodayAutoSaveReturn {
  const { debounceMs = 1000, onSuccess, onError } = options;

  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const debounceTimerRef = useRef<number | null>(null);
  const saveQueueRef = useRef<EntryFormData | null>(null);

  const performSave = useCallback(async (data: EntryFormData) => {
    // KRITICKÉ: Neukládej prázdný content
    if (!data.content || !data.content.trim()) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const response = await api.post<EntryDetail>('/entries/today/', data);
      setLastSaved(new Date());

      if (onSuccess) {
        onSuccess(response);
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
  }, [onSuccess, onError]);

  const save = useCallback((data: EntryFormData) => {
    // Uložit nejnovější data
    saveQueueRef.current = data;

    // Zrušit existující timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Nastavit nový timer
    debounceTimerRef.current = setTimeout(() => {
      if (saveQueueRef.current) {
        performSave(saveQueueRef.current);
        saveQueueRef.current = null;
      }
    }, debounceMs) as unknown as number;
  }, [debounceMs, performSave]);

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
