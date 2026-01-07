import type { MoodAnalytics } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';

interface MoodDistributionChartProps {
  data: MoodAnalytics | undefined;
}

/**
 * MoodDistributionChart displays the distribution of mood ratings (1-5) as a horizontal bar chart.
 * 
 * Uses a styled list approach similar to TagAnalyticsChart to show:
 * - Mood rating (1-5)
 * - Entry count for each rating
 * - Visual bar representing relative count
 * 
 * Highlights the most common mood with accent color, others use muted styling.
 * Follows brutalist "Analog Tech" design with hard shadows and sharp borders.
 */
export function MoodDistributionChart({ data }: MoodDistributionChartProps) {
  const { t } = useLanguage();

  // Handle empty or undefined data
  const distribution = data?.distribution;
  const hasData = distribution && Object.values(distribution).some(count => count > 0);

  if (!hasData) {
    return (
      <div className="border-2 border-border bg-bg-panel p-8 text-center rounded-none shadow-hard">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
          {t('statistics.moodDistribution.title')}
        </h3>
        <p className="text-text-muted font-mono text-sm">
          {t('statistics.moodDistribution.noData')}
        </p>
      </div>
    );
  }

  // Prepare data for display (ratings 1-5)
  const ratings = (['1', '2', '3', '4', '5'] as const).map(rating => ({
    rating: parseInt(rating, 10),
    count: distribution[rating],
  }));

  // Find max count for bar width calculation and to identify most common mood
  const maxCount = Math.max(...ratings.map(r => r.count));

  return (
    <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
        {t('statistics.moodDistribution.title')}
      </h3>

      <div className="space-y-3">
        {ratings.map(({ rating, count }) => {
          const barWidth = maxCount > 0 ? (count / maxCount) * 100 : 0;
          const isMostCommon = count === maxCount && count > 0;

          return (
            <div
              key={rating}
              className="relative border-2 border-border bg-bg-main p-3"
            >
              {/* Background bar showing relative count */}
              <div
                className="absolute inset-0 bg-accent transition-all duration-300"
                style={{
                  width: `${barWidth}%`,
                  opacity: isMostCommon ? 0.2 : 0.1,
                }}
              />

              {/* Content */}
              <div className="relative flex items-center justify-between gap-4">
                {/* Rating label */}
                <div className="flex items-center gap-3 min-w-0">
                  <span
                    className={`font-mono text-sm font-bold ${
                      isMostCommon ? 'text-accent' : 'text-text-main'
                    }`}
                  >
                    {t('statistics.moodDistribution.rating')} {rating}
                  </span>
                </div>

                {/* Count */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span
                    className={`text-xs font-mono font-bold ${
                      isMostCommon ? 'text-accent' : 'text-text-main'
                    }`}
                  >
                    {count}
                  </span>
                  <span className="text-[10px] font-mono text-text-muted uppercase tracking-widest">
                    {t('statistics.moodDistribution.entries')}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
