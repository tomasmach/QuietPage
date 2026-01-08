import type { StatisticsData } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';
import { MoodTrendBadge } from './MoodTrendBadge';

interface StatsSummaryCardsProps {
  data: StatisticsData;
}

export function StatsSummaryCards({ data }: StatsSummaryCardsProps) {
  const { t } = useLanguage();
  const { moodAnalytics, wordCountAnalytics } = data;

  const cards = [
    {
      label: t('statistics.summaryCards.avgMood'),
      value: moodAnalytics.average ? moodAnalytics.average.toFixed(1) : 'N/A',
      subtitle: `${moodAnalytics.totalRatedEntries} ${t('statistics.summaryCards.ratedEntries')}`,
      badge: <MoodTrendBadge trend={moodAnalytics.trend} />,
    },
    {
      label: t('statistics.summaryCards.totalWords'),
      value: wordCountAnalytics.total.toLocaleString(),
      subtitle: `${wordCountAnalytics.totalEntries} ${t('statistics.summaryCards.entries')}`,
    },
    {
      label: t('statistics.summaryCards.avgPerDay'),
      value: Math.round(wordCountAnalytics.averagePerDay).toLocaleString(),
      subtitle: t('statistics.summaryCards.words'),
    },
    {
      label: t('statistics.summaryCards.goalRate'),
      value: `${wordCountAnalytics.goalAchievementRate.toFixed(0)}%`,
      subtitle: t('statistics.summaryCards.daysMetGoal'),
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <div
          key={index}
          className="theme-aware border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none"
        >
          <p className="theme-aware text-xs font-bold uppercase tracking-widest text-text-muted font-mono mb-2">
            {card.label}
          </p>
          <div className="flex items-center gap-3">
            <p className="theme-aware text-3xl font-bold text-text-main font-mono">
              {card.value}
            </p>
            {'badge' in card && card.badge}
          </div>
          <p className="theme-aware text-xs text-text-muted font-mono mt-1">
            {card.subtitle}
          </p>
        </div>
      ))}
    </div>
  );
}
