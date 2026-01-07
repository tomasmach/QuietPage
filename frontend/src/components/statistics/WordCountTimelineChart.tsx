/**
 * Word count timeline chart component.
 *
 * Displays a timeline area chart showing daily word counts over a period.
 * Uses brutalist design with solid fill (no gradients) per styles.md guidelines.
 */
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { WordCountAnalytics } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';

interface WordCountTimelineChartProps {
  data: WordCountAnalytics;
}

export function WordCountTimelineChart({ data }: WordCountTimelineChartProps) {
  const { t, language } = useLanguage();
  const localeCode = language === 'cs' ? 'cs-CZ' : 'en-US';

  if (!data.timeline || data.timeline.length === 0) {
    return (
      <div className="border-2 border-border bg-bg-panel p-8 text-center rounded-none">
        <p className="text-text-muted font-mono text-sm">
          {t('statistics.wordCountTimeline.noData')}
        </p>
      </div>
    );
  }

  const chartData = data.timeline.map(day => ({
    date: new Date(day.date).toLocaleDateString(localeCode, { month: 'short', day: 'numeric' }),
    words: day.wordCount,
  }));

  return (
    <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
        {t('statistics.wordCountTimeline.title')}
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <CartesianGrid
            strokeDasharray="0"
            stroke="var(--color-border)"
            strokeWidth={1}
          />
          <XAxis
            dataKey="date"
            stroke="var(--color-text-main)"
            style={{ fontFamily: 'IBM Plex Mono', fontSize: '12px' }}
          />
          <YAxis
            stroke="var(--color-text-main)"
            style={{ fontFamily: 'IBM Plex Mono', fontSize: '12px' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-bg-panel)',
              border: '2px solid var(--color-border)',
              fontFamily: 'IBM Plex Mono',
              fontSize: '12px',
            }}
            formatter={(value: number | undefined) => [value ?? 0, t('statistics.wordCountTimeline.wordsLabel')]}
          />
          <Area
            type="monotone"
            dataKey="words"
            name={t('statistics.wordCountTimeline.wordsLabel')}
            stroke="var(--color-accent)"
            strokeWidth={2}
            fill="var(--color-accent)"
            fillOpacity={0.15}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
