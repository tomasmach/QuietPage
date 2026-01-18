import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { Card } from '../components/ui/Card';
import { Spinner } from '../components/ui/Spinner';
import { RecentEntries } from '../components/dashboard/RecentEntries';
import { WritingPrompt } from '../components/dashboard/WritingPrompt';
import { FeaturedEntry } from '../components/dashboard/FeaturedEntry';
import { WeeklyStats } from '../components/dashboard/WeeklyStats';
import { useDashboard } from '../hooks/useDashboard';
import { useLanguage } from '../contexts/LanguageContext';

export function DashboardPage() {
  const navigate = useNavigate();
  const { t, language } = useLanguage();
  const { data, isLoading, error, refreshFeaturedEntry, isRefreshingFeatured } = useDashboard();

  const handleNewEntry = () => {
    navigate('/write');
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
  const locale = language === 'en' ? 'en-US' : 'cs-CZ';
  const formattedDate = today.toLocaleDateString(locale, {
    day: 'numeric',
    month: 'long',
  });

  // Get time-based greeting key
  const hour = today.getHours();
  const getGreetingKey = () => {
    if (hour < 12) return 'morning';
    if (hour < 18) return 'afternoon';
    return 'evening';
  };
  const greetingKey = getGreetingKey();

  // Calculate progress percentage
  const progressPercentage = Math.min((data.stats.todayWords / data.stats.dailyGoal) * 100, 100);

  return (
    <AppLayout
      sidebar={<Sidebar />}
      contextPanel={
        <ContextPanel>
          <WeeklyStats
            weeklyStats={data.weeklyStats}
            currentStreak={data.stats.currentStreak}
          />
        </ContextPanel>
      }
    >
      <div className="p-8 space-y-8 relative">
        {/* Top Thin Progress Bar */}
        <div className="absolute top-0 left-0 w-full h-1 bg-bg-panel opacity-20">
          <div
            className="h-full bg-accent transition-all duration-500"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>

        {/* Header */}
        <div className="flex justify-between items-end border-b-2 border-border pb-4 border-dashed">
          <div>
            <div className="text-sm font-bold uppercase text-text-text-muted mb-1">
              {t(`dashboard.greeting.${greetingKey}`)}
            </div>
            <h1 className="text-3xl font-bold uppercase text-text-main">
              {formattedDate}
            </h1>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-text-main">{data.stats.todayWords}</div>
            <div className="text-sm font-bold uppercase text-text-text-muted">
              {t('meta.wordsToday')}
            </div>
          </div>
        </div>

        {/* Writing Prompt */}
        <WritingPrompt onStartWriting={handleNewEntry} />

        {/* Featured Entry (only shown if entry exists) */}
        {data.featuredEntry && (
          <FeaturedEntry
            entry={data.featuredEntry}
            onRefresh={refreshFeaturedEntry}
            isRefreshing={isRefreshingFeatured}
          />
        )}

        {/* Quote or Recent Entries */}
        {!data.hasEntries && data.quote ? (
          <Card className="text-center py-12">
            <blockquote className="space-y-4">
              <p className="text-xl italic text-text">"{data.quote.text}"</p>
              <footer className="text-text-muted">-- {data.quote.author}</footer>
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
