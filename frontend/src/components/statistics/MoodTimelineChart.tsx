import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { MoodAnalytics } from '../../types/statistics';

interface MoodTimelineChartProps {
  data: MoodAnalytics;
}

export function MoodTimelineChart({ data }: MoodTimelineChartProps) {
  if (!data.timeline || data.timeline.length < 2) {
    return (
      <div className="border-2 border-border bg-bg-panel p-8 text-center rounded-none">
        <p className="text-text-muted font-mono text-sm">
          NOT ENOUGH DATA TO DISPLAY MOOD TRENDS
        </p>
      </div>
    );
  }

  // Format data for Recharts
  const chartData = data.timeline.map(day => ({
    date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    mood: day.average,
  }));

  return (
    <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
        MOOD TIMELINE
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
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
            domain={[1, 5]}
            ticks={[1, 2, 3, 4, 5]}
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
          <Line
            type="monotone"
            dataKey="mood"
            stroke="var(--color-accent)"
            strokeWidth={2}
            dot={{ r: 4, fill: 'var(--color-accent)' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
