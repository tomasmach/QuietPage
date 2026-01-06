import { useState } from 'react';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { useStatistics } from '../hooks/useStatistics';
import { TimeRangeSelector } from '../components/statistics/TimeRangeSelector';
import { StatsSummaryCards } from '../components/statistics/StatsSummaryCards';
import { MoodTimelineChart } from '../components/statistics/MoodTimelineChart';
import { WordCountTimelineChart } from '../components/statistics/WordCountTimelineChart';
import { StatisticsLoading } from '../components/statistics/StatisticsLoading';
import { StatisticsError } from '../components/statistics/StatisticsError';
import type { PeriodType } from '../types/statistics';

export function StatsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>('30d');
  const { data, isLoading, error, refetch } = useStatistics(selectedPeriod);

  return (
    <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
      <div className="p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-4xl font-bold uppercase tracking-wide text-text-main font-mono">
            STATISTICS
          </h1>
        </div>

        {/* Time Range Selector */}
        <TimeRangeSelector
          selectedPeriod={selectedPeriod}
          onPeriodChange={setSelectedPeriod}
        />

        {/* Content */}
        {isLoading ? (
          <StatisticsLoading />
        ) : error ? (
          <StatisticsError error={error} onRetry={refetch} />
        ) : data ? (
          <div className="space-y-8">
            {/* Summary Cards */}
            <StatsSummaryCards data={data} />

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <MoodTimelineChart data={data.moodAnalytics} />
              <WordCountTimelineChart data={data.wordCountAnalytics} />
            </div>
          </div>
        ) : null}
      </div>
      <ThemeToggle />
    </AppLayout>
  );
}
