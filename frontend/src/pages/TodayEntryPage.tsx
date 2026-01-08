import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { Card } from '../components/ui/Card';
import { ProgressBar } from '../components/ui/ProgressBar';
import { MoodSelector } from '../components/journal/MoodSelector';
import { TagInput } from '../components/journal/TagInput';
import { useTodayEntry } from '../hooks/useTodayEntry';
import { useTodayAutoSave } from '../hooks/useTodayAutoSave';
import { useDashboard } from '../hooks/useDashboard';
import { useLanguage } from '../contexts/LanguageContext';

const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY_MS = 1000;

export function TodayEntryPage() {
  const navigate = useNavigate();
  const { t } = useLanguage();

  const { entry, isLoading, error, exists } = useTodayEntry();
  const { data: dashboardData } = useDashboard();
  const [content, setContent] = useState('');
  const [moodRating, setMoodRating] = useState<number | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [isCreatingEntry, setIsCreatingEntry] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [createError, setCreateError] = useState<Error | null>(null);
  
  const retryCountRef = useRef(0);
  const retryTimeoutRef = useRef<number | null>(null);

  // Auto-save functionality (bez refresh - není potřeba)
  const onSaveSuccess = useCallback(() => {
    // Reset retry count on successful save
    retryCountRef.current = 0;
    setCreateError(null);
    
    if (isCreatingEntry) {
      setIsCreatingEntry(false);
    }
  }, [isCreatingEntry]);

  const onSaveError = useCallback((err: Error, isCreating: boolean) => {
    // Always reset isCreatingEntry to unblock future attempts
    setIsCreatingEntry(false);
    
    // Only reset isInitialized during creation phase to allow retry
    // For normal auto-save failures, keep isInitialized=true to prevent re-creation
    if (isCreating) {
      retryCountRef.current += 1;
      
      if (retryCountRef.current >= MAX_RETRIES) {
        // Max retries reached - surface error UI
        setCreateError(err);
      } else {
        // Will retry in auto-create effect with exponential backoff
        setIsInitialized(false);
      }
    }
  }, []);

  const { save: autoSave, isSaving: isAutoSaving, lastSaved } = useTodayAutoSave({
    onSuccess: onSaveSuccess,
    onError: (err) => onSaveError(err, isCreatingEntry),
  });

  // Auto-create empty entry if it doesn't exist (750words.com style)
  // with exponential backoff on retry
  useEffect(() => {
    if (!isLoading && !exists && !error && !isCreatingEntry && !isInitialized && !createError) {
      const retryCount = retryCountRef.current;
      const delayMs = retryCount > 0 ? INITIAL_RETRY_DELAY_MS * Math.pow(2, retryCount - 1) : 0;
      
      retryTimeoutRef.current = setTimeout(() => {
        setIsCreatingEntry(true);
        setIsInitialized(true);
        // Create empty entry
        autoSave({
          content: '',
          mood_rating: null,
          tags: [],
        });
      }, delayMs) as unknown as number;
    }
    
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
        retryTimeoutRef.current = null;
      }
    };
  }, [isLoading, exists, error, isCreatingEntry, isInitialized, createError, autoSave]);

  // Initialize form from entry data POUZE JEDNOU
  useEffect(() => {
    if (entry && !isInitialized) {
      setContent(entry.content);
      setMoodRating(entry.mood_rating);
      setTags(entry.tags);
      setIsInitialized(true);
    }
  }, [entry, isInitialized]);

  // Auto-save when content changes (pouze když už je initialized)
  useEffect(() => {
    // Autosave JEN když už máme entry a je initialized
    // Debounce v useTodayAutoSave zajistí, že se volá až po 1s klidu
    if (isInitialized && !isCreatingEntry) {
      autoSave({
        content,
        mood_rating: moodRating,
        tags,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content, moodRating, tags]);

  // Word count
  const wordCount = content.trim().split(/\s+/).filter(Boolean).length;

  const handleCancel = () => {
    navigate('/dashboard');
  };

  if (isLoading) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8 flex items-center justify-center min-h-[50vh]">
          <Spinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8">
          <Card>
            <p className="text-error">
              {t('entry.loadError')}
            </p>
            <Button onClick={handleCancel} className="mt-4">
              {t('common.cancel')}
            </Button>
          </Card>
        </div>
      </AppLayout>
    );
  }

  // Show error UI when max retries reached during entry creation
  if (createError && retryCountRef.current >= MAX_RETRIES) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8">
          <Card>
            <p className="text-error font-bold mb-2">
              {t('entry.createError')}
            </p>
            <p className="text-text-muted mb-4">
              {t('entry.createErrorDetails').replace('{count}', String(MAX_RETRIES))}
            </p>
            <div className="flex gap-3">
              <Button 
                onClick={() => {
                  retryCountRef.current = 0;
                  setCreateError(null);
                  setIsInitialized(false);
                }} 
                variant="primary"
              >
                {t('entry.retryCreate')}
              </Button>
              <Button onClick={handleCancel} variant="secondary">
                {t('common.cancel')}
              </Button>
            </div>
          </Card>
        </div>
      </AppLayout>
    );
  }

  // Datum je vždy dnešek (ne entry.created_at)
  const date = new Date();

  // Greeting based on time of day
  const hour = new Date().getHours();
  const greetingKey = hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening';

  // Format date as "29. PROSINCE"
  const formattedDate = date.toLocaleDateString('cs-CZ', {
    day: 'numeric',
    month: 'long',
  }).toUpperCase();

  return (
    <AppLayout
      sidebar={<Sidebar />}
      contextPanel={
        <ContextPanel>
          <div className="space-y-6">
            {/* Progress */}
            {dashboardData && (
              <div>
                <ProgressBar
                  value={wordCount}
                  max={dashboardData.stats.dailyGoal}
                  showLabel={true}
                />
              </div>
            )}

            {/* Streak Badge */}
            {dashboardData && (
              <div className="border-2 border-border p-4 bg-bg-panel shadow-hard">
                <div className="flex justify-between items-stretch gap-4">
                  <div className="flex flex-col justify-between">
                    <span className="text-xs font-bold uppercase text-text-text-muted">
                      {t('meta.currentStreak')}
                    </span>
                    <div className="text-3xl font-bold text-text-main">{dashboardData.stats.currentStreak}</div>
                  </div>
                  <div className="flex items-center">
                    <Flame size={56} className="text-text-main" strokeWidth={1.2} />
                  </div>
                </div>
              </div>
            )}

            {/* Mood Selector */}
            <div>
              <h3 className="text-sm font-bold uppercase mb-4 border-b-2 border-border pb-1 text-text-main">
                {t('meta.moodCheck')}
              </h3>
              <MoodSelector
                value={moodRating as 1 | 2 | 3 | 4 | 5 | null}
                onChange={setMoodRating}
              />
            </div>

            {/* Tags */}
            <div>
              <h3 className="text-sm font-bold uppercase mb-4 border-b-2 border-border pb-1 text-text-main">
                {t('entry.tags')}
              </h3>
              <TagInput value={tags} onChange={setTags} />
            </div>

            {/* Actions */}
            <div className="space-y-3">
              <Button onClick={handleCancel} variant="secondary" className="w-full">
                {t('common.cancel')}
              </Button>
            </div>

            {/* Auto-save indicator */}
            {isAutoSaving && (
              <p className="text-sm text-text-muted">{t('entry.saving')}...</p>
            )}
            {lastSaved && !isAutoSaving && (
              <p className="text-sm text-text-muted">
                {t('entry.saved')}{' '}
                {lastSaved.toLocaleTimeString('cs-CZ', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            )}
          </div>
        </ContextPanel>
      }
    >
      <div className="p-12 bg-bg-panel flex flex-col" style={{ minHeight: 'calc(100vh - 0px)' }}>
        <div className="max-w-5xl mx-auto w-full flex flex-col flex-1">
          {/* Header */}
          <div className="mb-8 flex justify-between items-end border-b-2 border-border pb-4 border-dashed flex-shrink-0">
            <div>
              <div className="text-sm font-bold uppercase text-text-text-muted mb-1">
                {t(`dashboard.greeting.${greetingKey}`)}
              </div>
              <h1 className="text-3xl font-bold uppercase text-text-main">
                {formattedDate}
              </h1>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-text-main">{wordCount}</div>
              <div className="text-sm font-bold uppercase text-text-text-muted">
                {t('meta.wordsToday')}
              </div>
            </div>
          </div>

          {/* Editor */}
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={t('entry.contentPlaceholder')}
            spellCheck={false}
            className="w-full flex-1 text-lg font-mono font-medium leading-relaxed resize-none border-0 bg-transparent focus:ring-0 focus:outline-none text-text-main placeholder:text-text-text-muted"
            autoFocus
          />
        </div>
      </div>
    </AppLayout>
  );
}
