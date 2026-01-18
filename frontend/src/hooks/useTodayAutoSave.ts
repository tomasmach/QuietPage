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
  const flushImmediateRef = useRef<(() => void) | null>(null);

  // Use refs for callbacks to avoid dependency changes in performSave
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);

  // Keep refs up to date
  onSuccessRef.current = onSuccess;
  onErrorRef.current = onError;

  /**
   * Perform the actual save operation
   * Uses refs for callbacks to maintain stable identity
   */
  const performSave = useCallback(async (data: EntryFormData) => {
    // Povolit prázdný content pro 750words.com style
    // Backend vytvoří prázdný entry, streak se updatne až když má obsah

    setIsSaving(true);
    setError(null);

    try {
      const response = await api.post<EntryDetail>('/entries/today/', data);
      setLastSaved(new Date());

      if (onSuccessRef.current) {
        onSuccessRef.current(response);
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Auto-save failed');
      setError(error);

      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
    } finally {
      setIsSaving(false);
    }
  }, []);

  /**
   * Flush pending save immediately (for cleanup/unmount)
   * Uses fetch with keepalive for reliable background delivery
   */
  const flushImmediate = useCallback(() => {
    const pendingData = saveQueueRef.current;

    if (!pendingData) {
      return;
    }

    // Read CSRF token from cookie
    const getCsrfToken = (): string | null => {
      const cookies = document.cookie.split(';');
      const csrfCookie = cookies.find(cookie => cookie.trim().startsWith('csrftoken='));
      return csrfCookie ? csrfCookie.split('=')[1].trim() : null;
    };

    // Fire-and-forget fetch with keepalive for background delivery
    fetch('/api/v1/entries/today/', {
      method: 'POST',
      body: JSON.stringify(pendingData),
      keepalive: true,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...(getCsrfToken() && { 'X-CSRFToken': getCsrfToken()! })
      }
    }).catch(() => {});

    saveQueueRef.current = null;
  }, []);

  // Store the current flushImmediate in a ref for stable cleanup access
  flushImmediateRef.current = flushImmediate;

  /**
   * Debounced save function
   */
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

  /**
   * Cleanup on unmount - flush pending saves before clearing timer
   * Uses synchronous fire-and-forget pattern to avoid async cleanup issues
   */
  useEffect(() => {
    return () => {
      // Flush any pending save before unmounting
      flushImmediateRef.current?.();

      // Clear debounce timer
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
        debounceTimerRef.current = null;
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
