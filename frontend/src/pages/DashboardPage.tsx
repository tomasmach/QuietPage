import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { Card } from '../components/ui/Card';
import { Spinner } from '../components/ui/Spinner';
import { RecentEntries } from '../components/dashboard/RecentEntries';
import { StatsPanel } from '../components/dashboard/StatsPanel';
import { WordCount } from '../components/journal/WordCount';
import { useDashboard } from '../hooks/useDashboard';
import { useLanguage } from '../contexts/LanguageContext';

export function DashboardPage() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const { data, isLoading, error } = useDashboard();
  const [selectedMood, setSelectedMood] = useState<number | null>(null);

  const handleNewEntry = () => {
    navigate('/entries/new');
  };

  const handleMoodSelect = (mood: number) => {
    setSelectedMood(mood);
    // In a real app, this would create/update today's entry with the mood
    // For now, just store it in local state
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

  if (error || !data) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8">
          <Card>
            <p className="text-error">
              Chyba pri nacitani dashboardu: {error?.message || 'Neznama chyba'}
            </p>
          </Card>
        </div>
      </AppLayout>
    );
  }

  // Get current date info
  const today = new Date();
  const formattedDate = today.toLocaleDateString('cs-CZ', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return (
    <AppLayout
      sidebar={<Sidebar />}
      contextPanel={
        <ContextPanel>
          <StatsPanel
            stats={data.stats}
            onMoodSelect={handleMoodSelect}
            selectedMood={selectedMood}
          />
        </ContextPanel>
      }
    >
      <div className="p-8 space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-primary mb-2">{data.greeting}</h1>
          <div className="flex items-center gap-4">
            <p className="text-muted">{formattedDate}</p>
            {data.stats.todayWords > 0 && (
              <>
                <span className="text-muted">•</span>
                <WordCount current={data.stats.todayWords} />
              </>
            )}
          </div>
        </div>

        {/* Quote or Recent Entries */}
        {!data.hasEntries && data.quote ? (
          <Card className="text-center py-12">
            <blockquote className="space-y-4">
              <p className="text-xl italic text-text">"{data.quote.text}"</p>
              <footer className="text-muted">-- {data.quote.author}</footer>
            </blockquote>
            <div className="mt-8">
              <button
                onClick={handleNewEntry}
                className="px-6 py-3 bg-accent text-bg-panel font-bold border-2 border-border shadow-hard hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all"
              >
                {t('dashboard.newEntry')}
              </button>
            </div>
          </Card>
        ) : (
          <RecentEntries entries={data.recentEntries} onNewEntry={handleNewEntry} />
        )}
      </div>
    </AppLayout>
  );
}
