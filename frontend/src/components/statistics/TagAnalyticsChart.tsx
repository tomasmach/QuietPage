import type { TagAnalytics } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';

interface TagAnalyticsChartProps {
  data: TagAnalytics | undefined;
}

/**
 * TagAnalyticsChart displays top 10 tags by entry count with their metrics.
 * 
 * Uses a styled list approach (vs. bar chart) to show multiple metrics per tag:
 * - Entry count
 * - Average words per entry
 * - Average mood (if available)
 * 
 * Follows brutalist "Analog Tech" design with hard shadows and sharp borders.
 */
export function TagAnalyticsChart({ data }: TagAnalyticsChartProps) {
  const { t } = useLanguage();

  // Handle empty or undefined data
  if (!data || data.tags.length === 0) {
    return (
      <div className="theme-aware border-2 border-border bg-bg-panel p-8 text-center rounded-none shadow-hard">
        <h3 className="theme-aware text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
          {t('statistics.tagAnalytics.title')}
        </h3>
        <p className="theme-aware text-text-muted font-mono text-sm">
          {t('statistics.tagAnalytics.noTags')}
        </p>
      </div>
    );
  }

  // Sort by entry count (descending) and take top 10
  const topTags = [...data.tags]
    .sort((a, b) => b.entryCount - a.entryCount)
    .slice(0, 10);

  // Find max entry count for bar width calculation
  const maxEntryCount = topTags[0]?.entryCount || 1;

  return (
    <div className="theme-aware border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="theme-aware text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
        {t('statistics.tagAnalytics.title')}
      </h3>

      <div className="space-y-3">
        {topTags.map((tag, index) => {
          const barWidth = (tag.entryCount / maxEntryCount) * 100;
          const isTop = index === 0;

          return (
            <div
              key={tag.name}
              className="theme-aware relative border-2 border-border bg-bg-main p-3"
            >
              {/* Background bar showing relative entry count */}
              <div
                className="theme-aware absolute inset-0 bg-accent transition-all duration-300"
                style={{
                  width: `${barWidth}%`,
                  opacity: isTop ? 0.2 : 0.1,
                }}
              />

              {/* Content */}
              <div className="relative flex items-center justify-between gap-4">
                {/* Tag name and entry count */}
                <div className="flex items-center gap-3 min-w-0">
                  <span
                    className={`theme-aware font-mono text-sm font-bold truncate ${
                      isTop ? 'text-accent' : 'text-text-main'
                    }`}
                  >
                    #{tag.name}
                  </span>
                  <span className="theme-aware text-[10px] font-mono text-text-muted uppercase tracking-widest whitespace-nowrap">
                    {tag.entryCount} {t('statistics.tagAnalytics.entries')}
                  </span>
                </div>

                {/* Metrics */}
                <div className="flex items-center gap-4 flex-shrink-0">
                  {/* Average words */}
                  <div className="text-right">
                    <span className="theme-aware text-xs font-mono font-bold text-text-main">
                      {Math.round(tag.averageWords)}
                    </span>
                    <span className="theme-aware text-[10px] font-mono text-text-muted uppercase tracking-widest ml-1">
                      {t('statistics.tagAnalytics.avgWords')}
                    </span>
                  </div>

                  {/* Average mood (only if available) */}
                  {tag.averageMood !== null && (
                    <div className="theme-aware text-right border-l-2 border-border pl-4">
                      <span className="theme-aware text-xs font-mono font-bold text-text-main">
                        {tag.averageMood.toFixed(1)}
                      </span>
                      <span className="theme-aware text-[10px] font-mono text-text-muted uppercase tracking-widest ml-1">
                        {t('statistics.tagAnalytics.avgMood')}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Total tags footer */}
      {data.totalTags > 10 && (
        <div className="theme-aware mt-4 pt-4 border-t-2 border-border">
          <p className="theme-aware text-[10px] font-mono text-text-muted uppercase tracking-widest text-center">
            {t('statistics.tagAnalytics.title')}: {data.totalTags}
          </p>
        </div>
      )}
    </div>
  );
}
