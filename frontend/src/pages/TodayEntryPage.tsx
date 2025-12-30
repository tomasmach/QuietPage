import { useCallback, useEffect, useState } from 'react';
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

export function TodayEntryPage() {
  const navigate = useNavigate();
  const { t } = useLanguage();

  const { entry, isLoading, error } = useTodayEntry();
  const { data: dashboardData } = useDashboard();
  const [content, setContent] = useState('');
  const [moodRating, setMoodRating] = useState<number | null>(null);
  const [tags, setTags] = useState<string[]>([]);

  // Auto-save functionality
  const onSaveSuccess = useCallback(() => {
    // Záznam uložen - zůstáváme na /write (nenavigujeme)
  }, []);

  const { save: autoSave, isSaving: isAutoSaving, lastSaved } = useTodayAutoSave({
    onSuccess: onSaveSuccess,
  });

  // Initialize form from entry data
  useEffect(() => {
    if (entry) {
      setContent(entry.content);
      setMoodRating(entry.mood_rating);
      setTags(entry.tags);
    }
  }, [entry]);

  // Auto-save when content changes
  useEffect(() => {
    // Only autosave if content is non-empty
    if (content && content.trim()) {
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
              Chyba pri nacitani zaznamu: {error.message}
            </p>
            <Button onClick={handleCancel} className="mt-4">
              {t('common.cancel')}
            </Button>
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
      <div className="p-12 bg-bg-panel min-h-screen">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-end border-b-2 border-border pb-4 border-dashed">
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
            rows={20}
            spellCheck={false}
            className="w-full text-lg font-mono font-medium leading-relaxed resize-none border-0 bg-transparent focus:ring-0 focus:outline-none text-text-main placeholder:text-text-text-muted"
            autoFocus
          />
        </div>
      </div>
    </AppLayout>
  );
}
