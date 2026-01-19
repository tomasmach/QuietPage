import { useState } from 'react';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { SEO } from '../components/SEO';
import { useStatistics } from '../hooks/useStatistics';
import { TimeRangeSelector } from '../components/statistics/TimeRangeSelector';
import { StatsSummaryCards } from '../components/statistics/StatsSummaryCards';
import { MoodTimelineChart } from '../components/statistics/MoodTimelineChart';
import { MoodDistributionChart } from '../components/statistics/MoodDistributionChart';
import { WordCountTimelineChart } from '../components/statistics/WordCountTimelineChart';
import { FrequencyHeatmap } from '../components/statistics/FrequencyHeatmap';
import { TimeOfDayChart } from '../components/statistics/TimeOfDayChart';
import { DayOfWeekChart } from '../components/statistics/DayOfWeekChart';
import { StreakHistoryList } from '../components/statistics/StreakHistoryList';
import { TagAnalyticsChart } from '../components/statistics/TagAnalyticsChart';
import { BestDayHighlight } from '../components/statistics/BestDayHighlight';
import { MilestonesGrid } from '../components/statistics/MilestonesGrid';
import { GoalStreakCard } from '../components/statistics/GoalStreakCard';
import { PersonalRecordsCard } from '../components/statistics/PersonalRecordsCard';
import { StatisticsLoading } from '../components/statistics/StatisticsLoading';
import { StatisticsError } from '../components/statistics/StatisticsError';
import { useLanguage } from '../contexts/LanguageContext';
import { cn } from '../lib/utils';
import type { PeriodType } from '../types/statistics';

type ViewMode = 'milestones' | 'patterns';

const VIEW_MODE_BASE_CLASSES =
  'px-6 py-3 font-mono text-sm font-bold uppercase tracking-widest border-2 border-border transition-all duration-150 rounded-none';

function getViewModeClasses(isActive: boolean): string {
  if (isActive) {
    return cn(VIEW_MODE_BASE_CLASSES, 'bg-accent text-accent-fg shadow-hard');
  }
  return cn(
    VIEW_MODE_BASE_CLASSES,
    'bg-bg-panel text-text-main hover:shadow-hard hover:translate-x-[2px] hover:translate-y-[2px]'
  );
}

export function StatsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>('30d');
  const [viewMode, setViewMode] = useState<ViewMode>('milestones');
  const { data, isLoading, error, refetch } = useStatistics(selectedPeriod);
  const { t } = useLanguage();

  return (
    <>
      <SEO
        title="Statistics"
        description="View your writing statistics, mood analytics, streaks, and patterns over time."
      />
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
      <div className="p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-4xl font-bold uppercase tracking-wide text-text-main font-mono">
            {t('statistics.title')}
          </h1>
        </div>

        {/* Time Range Selector */}
        <TimeRangeSelector
          selectedPeriod={selectedPeriod}
          onPeriodChange={setSelectedPeriod}
        />

        {/* View Mode Toggle */}
        <div className="flex gap-3">
          <button
            onClick={() => setViewMode('milestones')}
            className={getViewModeClasses(viewMode === 'milestones')}
          >
            {t('statistics.viewModes.milestones')}
          </button>
          <button
            onClick={() => setViewMode('patterns')}
            className={getViewModeClasses(viewMode === 'patterns')}
          >
            {t('statistics.viewModes.patterns')}
          </button>
        </div>

        {/* Content */}
        {isLoading ? (
          <StatisticsLoading />
        ) : error ? (
          <StatisticsError error={error} onRetry={refetch} />
        ) : data ? (
          <div className="space-y-8">
            {/* Summary Cards - Always visible */}
            <StatsSummaryCards data={data} />

            {/* Best Day Highlight & Goal Streak - Always visible */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <BestDayHighlight data={data.wordCountAnalytics.bestDay ?? undefined} />
              <GoalStreakCard data={data.goalStreak} />
            </div>

            {/* Conditional Content based on viewMode */}
            {viewMode === 'milestones' ? (
              /* Milestones & Charts */
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Column: Milestones */}
                <MilestonesGrid data={data.milestones} />

                {/* Right Column: Personal Records + Charts */}
                <div className="space-y-8">
                  <PersonalRecordsCard data={data.personalRecords} />
                  <MoodTimelineChart data={data.moodAnalytics} />
                  <WordCountTimelineChart data={data.wordCountAnalytics} />
                  <MoodDistributionChart data={data.moodAnalytics} />
                </div>
              </div>
            ) : (
              /* Writing Patterns Grid */
              <div className="space-y-8">
                {/* Full width heatmap */}
                <FrequencyHeatmap />
                
                {/* Two column grid for all charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <TimeOfDayChart data={data.writingPatterns} />
                  <DayOfWeekChart data={data.writingPatterns} />
                  <StreakHistoryList data={data.writingPatterns} />
                  <TagAnalyticsChart data={data.tagAnalytics} />
                </div>
              </div>
            )}
          </div>
        ) : null}
      </div>
      <ThemeToggle />
    </AppLayout>
    </>
  );
}
