import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';
import type { Props as LabelProps } from 'recharts/types/component/Label';
import type { WritingPatterns } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';

interface DayOfWeekChartProps {
  data: WritingPatterns;
}

interface ChartDataPoint {
  day: string;
  fullDay: string;
  count: number;
  isMax: boolean;
}

/** Props interface for Recharts custom tooltip component */
interface CustomTooltipProps {
  active?: boolean;
  payload?: ReadonlyArray<{
    payload: ChartDataPoint;
  }>;
}

/** Props interface for Recharts custom label component, extending base Label props */
interface CustomLabelProps extends LabelProps {
  payload?: ChartDataPoint;
}

/**
 * DayOfWeekChart displays writing activity per day of the week using a bar chart.
 * 
 * Key principles (per 750words.com philosophy):
 * - Shows number of unique DAYS written (not entry count)
 * - Multiple entries per day = 1 writing day
 * - Highlights the most productive day with visual emphasis
 * - Uses accent color for all bars with special highlight for max
 */
export function DayOfWeekChart({ data }: DayOfWeekChartProps) {
  const { t } = useLanguage();

  // Define day order (Monday-Sunday)
  const dayOrder = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
  
  // Check if there's any data to display
  const hasData = Object.values(data.dayOfWeek).some(value => value > 0);

  // Find the maximum count to highlight the most productive day
  const maxCount = Math.max(...Object.values(data.dayOfWeek));

  // Prepare data for Recharts
  const chartData: ChartDataPoint[] = dayOrder.map(day => ({
    day: t(`statistics.dayOfWeekChart.${day}Abbr`),
    fullDay: t(`statistics.dayOfWeekChart.${day}`),
    count: data.dayOfWeek[day] || 0,
    isMax: data.dayOfWeek[day] === maxCount && maxCount > 0,
  }));

  // Custom tooltip to show full day name and count
  const renderTooltip = ({ active, payload }: CustomTooltipProps) => {
    if (!active || !payload || !payload.length) return null;

    const tooltipData = payload[0].payload;

    return (
      <div className="bg-bg-panel border-2 border-border px-4 py-3 shadow-hard">
        <p className="text-xs font-mono font-bold text-text-main uppercase tracking-wide mb-1">
          {tooltipData.fullDay}
        </p>
        <p className="text-xs font-mono text-text-muted">
          {tooltipData.count} {tooltipData.count === 1 
            ? t('statistics.dayOfWeekChart.daySingular') 
            : t('statistics.dayOfWeekChart.daysPlural')}
        </p>
        {tooltipData.isMax && (
          <p className="text-[10px] font-mono text-accent mt-1 font-bold uppercase tracking-wide">
            {t('statistics.dayOfWeekChart.mostProductive')}
          </p>
        )}
      </div>
    );
  };

  // Custom label to display count on top of bar for the max value
  const renderLabel = ({ x, y, width, value, payload }: CustomLabelProps) => {
    if (!payload?.isMax) return null;
    
    const xNum = typeof x === 'number' ? x : 0;
    const yNum = typeof y === 'number' ? y : 0;
    const widthNum = typeof width === 'number' ? width : 0;

    return (
      <g>
        <text
          x={xNum + widthNum / 2}
          y={yNum - 8}
          fill="var(--color-accent)"
          textAnchor="middle"
          className="font-mono text-xs font-bold"
        >
          {value}
        </text>
      </g>
    );
  };

  if (!hasData) {
    return (
      <div className="border-2 border-border bg-bg-panel p-8 text-center rounded-none shadow-hard">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
          {t('statistics.dayOfWeekChart.title')}
        </h3>
        <p className="text-text-muted font-mono text-sm">
          {t('statistics.dayOfWeekChart.notEnoughData')}
        </p>
      </div>
    );
  }

  return (
    <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
        {t('statistics.dayOfWeekChart.title')}
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart 
          data={chartData}
          margin={{ top: 20, right: 20, bottom: 5, left: 0 }}
        >
          <CartesianGrid
            strokeDasharray="0"
            stroke="var(--color-border)"
            strokeWidth={1}
            strokeOpacity={0.3}
            vertical={false}
          />
          <XAxis
            dataKey="day"
            stroke="var(--color-text-main)"
            style={{ fontFamily: 'IBM Plex Mono', fontSize: '12px' }}
            tickLine={false}
            axisLine={{ stroke: 'var(--color-border)', strokeWidth: 2 }}
          />
          <YAxis
            stroke="var(--color-text-main)"
            style={{ fontFamily: 'IBM Plex Mono', fontSize: '12px' }}
            tickLine={false}
            axisLine={{ stroke: 'var(--color-border)', strokeWidth: 2 }}
            label={{ 
              value: t('statistics.dayOfWeekChart.yAxisLabel'), 
              angle: -90, 
              position: 'insideLeft',
              style: { 
                fontFamily: 'IBM Plex Mono', 
                fontSize: '10px', 
                fill: 'var(--color-text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
              }
            }}
          />
          <Tooltip content={renderTooltip} cursor={{ fill: 'transparent' }} />
          <Bar 
            dataKey="count" 
            radius={[0, 0, 0, 0]}
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`}
                fill={entry.isMax ? 'var(--color-accent)' : 'var(--color-text-muted)'}
                stroke="var(--color-border)"
                strokeWidth={2}
                opacity={entry.isMax ? 1 : 0.6}
              />
            ))}
            <LabelList content={renderLabel} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Most productive day annotation */}
      {maxCount > 0 && (
        <div className="mt-4 pt-4 border-t-2 border-border">
          <p className="text-[10px] font-mono text-text-muted uppercase tracking-widest">
            {t('statistics.dayOfWeekChart.mostProductiveDay')}
          </p>
          <p className="text-sm font-mono font-bold text-accent mt-1">
            {chartData.find(d => d.isMax)?.fullDay} ({maxCount} {maxCount === 1 
              ? t('statistics.dayOfWeekChart.daySingular')
              : t('statistics.dayOfWeekChart.daysPlural')})
          </p>
        </div>
      )}
    </div>
  );
}
