import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Flame } from 'lucide-react';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { Card } from '../components/ui/Card';
import { useEntry } from '../hooks/useEntry';
import { useDashboard } from '../hooks/useDashboard';
import { useLanguage } from '../contexts/LanguageContext';

const MOOD_LABELS = {
  1: 'Terrible',
  2: 'Bad',
  3: 'Okay',
  4: 'Good',
  5: 'Great',
} as const;

export function EntryViewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t, language } = useLanguage();

  const { entry, isLoading, error } = useEntry(id);
  const { data: dashboardData } = useDashboard();
  const [content, setContent] = useState('');
  const [moodRating, setMoodRating] = useState<number | null>(null);
  const [tags, setTags] = useState<string[]>([]);

  // Initialize form from entry data
  useEffect(() => {
    if (entry) {
      setContent(entry.content);
      setMoodRating(entry.mood_rating);
      setTags(entry.tags);
    }
  }, [entry]);

  // Word count
  const wordCount = content.trim().split(/\s+/).filter(Boolean).length;

  const handleBackToArchive = () => {
    navigate('/archive');
  };

  if (isLoading && id) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8 flex items-center justify-center min-h-[50vh]">
          <Spinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  if (error && id) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8">
          <Card>
            <p className="text-error">
              {t('entry.loadError')}
            </p>
            <Button onClick={handleBackToArchive} className="mt-4">
              <ArrowLeft size={16} className="mr-2" />
              {t('common.cancel')}
            </Button>
          </Card>
        </div>
      </AppLayout>
    );
  }

  const date = entry
    ? new Date(entry.created_at)
    : new Date();

  // Map language to locale (cs -> cs-CZ, en -> en-US)
  const locale = language === 'cs' ? 'cs-CZ' : language === 'en' ? 'en-US' : (navigator.language || 'en-US');

  // Format date as "29. PROSINCE"
  const formattedDate = date.toLocaleDateString(locale, {
    day: 'numeric',
    month: 'long',
  }).toUpperCase();

  return (
    <AppLayout
      sidebar={<Sidebar />}
      contextPanel={
        <ContextPanel>
          <div className="space-y-6">
            {/* Streak Badge */}
            {dashboardData && (
              <div className="border-2 border-border p-3 bg-bg-panel shadow-hard">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] font-bold uppercase text-text-muted">
                    {t('meta.currentStreak')}
                  </span>
                  <Flame size={14} className="text-text-main" />
                </div>
                <div className="text-3xl font-bold text-text-main">{dashboardData.stats.currentStreak}</div>
              </div>
            )}

            {/* Mood Display */}
            {moodRating && (
              <div>
                <h3 className="text-xs font-bold uppercase mb-4 border-b-2 border-border pb-1 text-text-main">
                  {t('meta.moodCheck')}
                </h3>
                <div className="border-2 border-border p-3 bg-bg-panel shadow-hard">
                  <div className="text-sm font-bold text-text-main">
                    {MOOD_LABELS[moodRating as keyof typeof MOOD_LABELS]}
                  </div>
                </div>
              </div>
            )}

            {/* Tags Display */}
            {tags.length > 0 && (
              <div>
                <h3 className="text-xs font-bold uppercase mb-4 border-b-2 border-border pb-1 text-text-main">
                  {t('entry.tags')}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <div
                      key={tag}
                      className="border-2 border-border px-2 py-1 bg-bg-panel shadow-hard text-xs font-bold text-text-main"
                    >
                      {tag}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="space-y-3">
              <Button
                onClick={handleBackToArchive}
                variant="secondary"
                className="w-full"
              >
                <ArrowLeft size={16} className="mr-2" />
                Back to Archive
              </Button>
            </div>
          </div>
        </ContextPanel>
      }
    >
      <div className="p-12 bg-bg-panel min-h-screen">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-end border-b-2 border-border pb-4 border-dashed">
            <div>
              <div className="text-xs font-bold uppercase text-text-muted mb-1">
                Entry from
              </div>
              <h1 className="text-3xl font-bold uppercase text-text-main">
                {formattedDate}
              </h1>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-text-main">{wordCount}</div>
              <div className="text-[10px] font-bold uppercase text-text-muted">
                {t('meta.wordsToday')}
              </div>
            </div>
          </div>

          {/* Content Display */}
          <div className="prose prose-lg max-w-none">
            <div className="text-lg font-mono font-medium leading-relaxed text-text-main whitespace-pre-wrap">
              {content || <span className="text-text-muted italic">No content</span>}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
