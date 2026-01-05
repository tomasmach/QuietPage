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
 * Povolit prázdný content pro 750words.com style - jeden záznam na den.
 * Streak se updatne až když entry má skutečný obsah.
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
    // Povolit prázdný content pro 750words.com style
    // Backend vytvoří prázdný entry, streak se updatne až když má obsah

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
      // Flush pending save before unmount
      if (debounceTimerRef.current) {
        // Cancel the debounce timer
        clearTimeout(debounceTimerRef.current);
        debounceTimerRef.current = null;

        // Immediately invoke pending save if data exists
        if (saveQueueRef.current) {
          const pendingData = saveQueueRef.current;
          saveQueueRef.current = null;

          // Fire-and-forget immediate save, swallow errors
          performSave(pendingData).catch((err) => {
            // Log error but don't throw during unmount
            console.error('Failed to flush pending save on unmount:', err);
          });
        }
      }
    };
  }, [performSave]);

  return {
    save,
    isSaving,
    lastSaved,
    error,
  };
}
