import type { StatisticsData } from '../../types/statistics';

interface StatsSummaryCardsProps {
  data: StatisticsData;
}

export function StatsSummaryCards({ data }: StatsSummaryCardsProps) {
  const { moodAnalytics, wordCountAnalytics } = data;

  const cards = [
    {
      label: 'AVG MOOD',
      value: moodAnalytics.average ? moodAnalytics.average.toFixed(1) : 'N/A',
      subtitle: `${moodAnalytics.totalRatedEntries} rated entries`,
    },
    {
      label: 'TOTAL WORDS',
      value: wordCountAnalytics.total.toLocaleString(),
      subtitle: `${wordCountAnalytics.totalEntries} entries`,
    },
    {
      label: 'AVG PER DAY',
      value: Math.round(wordCountAnalytics.averagePerDay).toLocaleString(),
      subtitle: 'words',
    },
    {
      label: 'GOAL RATE',
      value: `${wordCountAnalytics.goalAchievementRate.toFixed(0)}%`,
      subtitle: 'days met goal',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <div
          key={index}
          className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none"
        >
          <p className="text-xs font-bold uppercase tracking-widest text-text-muted font-mono mb-2">
            {card.label}
          </p>
          <p className="text-3xl font-bold text-text-main font-mono">
            {card.value}
          </p>
          <p className="text-xs text-text-muted font-mono mt-1">
            {card.subtitle}
          </p>
        </div>
      ))}
    </div>
  );
}
