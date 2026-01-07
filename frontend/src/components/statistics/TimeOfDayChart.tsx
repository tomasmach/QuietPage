import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { WritingPatterns } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';

interface TimeOfDayChartProps {
  data: WritingPatterns;
}

interface ChartData {
  name: string;
  value: number;
  color: string;
  description: string;
  [key: string]: string | number; // Index signature for Recharts compatibility
}

/** Props interface for Recharts custom tooltip component */
interface CustomTooltipProps {
  active?: boolean;
  payload?: ReadonlyArray<{
    payload: ChartData;
  }>;
}

/**
 * TimeOfDayChart displays the distribution of entries across different times of day
 * as a donut chart with distinct colors for each period.
 * 
 * Time periods:
 * - Morning: 5 AM - 12 PM (warm yellow/orange)
 * - Afternoon: 12 PM - 6 PM (bright orange)
 * - Evening: 6 PM - 12 AM (deep purple)
 * - Night: 12 AM - 5 AM (dark blue)
 */
export function TimeOfDayChart({ data }: TimeOfDayChartProps) {
  const { t } = useLanguage();

  // Define colors for each time period following the brutalist design system
  // NOTE: These are semantic colors representing actual time periods (warm morning → cool night)
  // This is an exception to the monochrome design system due to the semantic nature of the data
  // For non-semantic charts, use var(--color-accent) and var(--color-text-muted) per styles.md
  const TIME_COLORS = {
    morning: '#F59E0B',   // Warm amber - sunrise/morning light
    afternoon: '#FB923C', // Bright orange - midday sun
    evening: '#8B5CF6',   // Deep purple - twilight
    night: '#3B82F6',     // Blue - night sky
  };

  // Check if there's any data to display
  const hasData = Object.values(data.timeOfDay).some(value => value > 0);

  // Prepare data for Recharts
  const chartData: ChartData[] = [
    {
      name: t('statistics.timeOfDayChart.morning'),
      value: data.timeOfDay.morning,
      color: TIME_COLORS.morning,
      description: t('statistics.timeOfDayChart.morningDesc'),
    },
    {
      name: t('statistics.timeOfDayChart.afternoon'),
      value: data.timeOfDay.afternoon,
      color: TIME_COLORS.afternoon,
      description: t('statistics.timeOfDayChart.afternoonDesc'),
    },
    {
      name: t('statistics.timeOfDayChart.evening'),
      value: data.timeOfDay.evening,
      color: TIME_COLORS.evening,
      description: t('statistics.timeOfDayChart.eveningDesc'),
    },
    {
      name: t('statistics.timeOfDayChart.night'),
      value: data.timeOfDay.night,
      color: TIME_COLORS.night,
      description: t('statistics.timeOfDayChart.nightDesc'),
    },
  ];

  // Calculate total for percentage calculation
  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  // Custom label to display percentage on each segment
  const renderLabel = (props: { value: number }): string => {
    const percentage = total > 0 ? ((props.value / total) * 100).toFixed(0) : '0';
    return props.value > 0 ? `${percentage}%` : '';
  };

  // Custom legend renderer with time period descriptions
  const renderLegend = () => {
    return (
      <div className="flex flex-col gap-2 mt-4">
        {chartData.map((entry) => (
          <div key={entry.name} className="flex items-center gap-3">
            <div
              className="w-4 h-4 border-2 border-border flex-shrink-0"
              style={{ backgroundColor: entry.color }}
            />
            <div className="flex-1">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-mono font-bold text-text-main uppercase tracking-wide">
                  {entry.name}
                </span>
                <span className="text-xs font-mono text-text-muted">
                  {entry.value} {t('statistics.timeOfDayChart.entries')}
                </span>
              </div>
              <p className="text-[10px] font-mono text-text-muted mt-0.5">
                {entry.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Custom tooltip
  const renderTooltip = ({ active, payload }: CustomTooltipProps) => {
    if (!active || !payload || !payload.length) return null;

    const tooltipData = payload[0].payload;
    const percentage = total > 0 ? ((tooltipData.value / total) * 100).toFixed(1) : '0.0';

    return (
      <div className="bg-bg-panel border-2 border-border px-4 py-3 shadow-hard">
        <p className="text-xs font-mono font-bold text-text-main uppercase tracking-wide mb-1">
          {tooltipData.name}
        </p>
        <p className="text-xs font-mono text-text-muted">
          {tooltipData.value} {t('statistics.timeOfDayChart.entries')} ({percentage}%)
        </p>
        <p className="text-[10px] font-mono text-text-muted mt-1">
          {tooltipData.description}
        </p>
      </div>
    );
  };

  if (!hasData) {
    return (
      <div className="border-2 border-border bg-bg-panel p-8 text-center rounded-none shadow-hard">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
          {t('statistics.timeOfDayChart.title')}
        </h3>
        <p className="text-text-muted font-mono text-sm">
          {t('statistics.timeOfDayChart.notEnoughData')}
        </p>
      </div>
    );
  }

  return (
    <div className="border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="text-xs font-bold uppercase tracking-widest text-text-main mb-4 font-mono">
        {t('statistics.timeOfDayChart.title')}
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
            label={renderLabel}
            labelLine={false}
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.color}
                stroke="var(--color-border)"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip content={renderTooltip} />
          <Legend content={renderLegend} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
