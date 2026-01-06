import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { WordCountAnalytics } from '../../types/statistics';

interface WordCountTimelineChartProps {
  data: WordCountAnalytics;
}

export function WordCountTimelineChart({ data }: WordCountTimelineChartProps) {
  if (!data.timeline || data.timeline.length === 0) {
    return (
      <div className="border-2 border-border bg-bg-panel p-8 text-center rounded-none">
        <p className="text-text-muted font-mono text-sm">
          NO WRITING DATA AVAILABLE
        </p>
      </div>
    );
  }

  const chartData = data.timeline.map(day => ({
    date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    words: day.wordCount,
  }));

  return (
    <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
        WORD COUNT TIMELINE
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="wordCountGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--color-accent)" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="var(--color-accent)" stopOpacity={0}/>
            </linearGradient>
          </defs>
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
          />
          <Area
            type="monotone"
            dataKey="words"
            stroke="var(--color-accent)"
            strokeWidth={2}
            fill="url(#wordCountGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
