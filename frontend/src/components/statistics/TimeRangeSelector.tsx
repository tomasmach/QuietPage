import { type PeriodType } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';

interface TimeRangeSelectorProps {
  selectedPeriod: PeriodType;
  onPeriodChange: (period: PeriodType) => void;
}

const PERIOD_KEYS: { value: PeriodType; labelKey: string }[] = [
  { value: '7d', labelKey: 'statistics.timeRange.last7Days' },
  { value: '30d', labelKey: 'statistics.timeRange.last30Days' },
  { value: '90d', labelKey: 'statistics.timeRange.last90Days' },
  { value: '1y', labelKey: 'statistics.timeRange.lastYear' },
  { value: 'all', labelKey: 'statistics.timeRange.allTime' },
];

export function TimeRangeSelector({ selectedPeriod, onPeriodChange }: TimeRangeSelectorProps) {
  const { t } = useLanguage();

  return (
    <div className="flex gap-4 font-mono">
      {PERIOD_KEYS.map(({ value, labelKey }) => (
        <button
          key={value}
          onClick={() => onPeriodChange(value)}
          className={`
            px-4 py-2 border-2 border-border rounded-none
            text-xs font-bold uppercase tracking-widest
            transition-all duration-150
            ${selectedPeriod === value
              ? 'bg-accent text-accent-fg shadow-hard translate-x-[2px] translate-y-[2px]'
              : 'bg-bg-panel text-text-main hover:shadow-hard hover:translate-x-[2px] hover:translate-y-[2px]'
            }
          `}
        >
          {t(labelKey)}
        </button>
      ))}
    </div>
  );
}
