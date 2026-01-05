import { type PeriodType } from '../../types/statistics';

interface TimeRangeSelectorProps {
  selectedPeriod: PeriodType;
  onPeriodChange: (period: PeriodType) => void;
}

const PERIODS: { value: PeriodType; label: string }[] = [
  { value: '7d', label: 'LAST 7 DAYS' },
  { value: '30d', label: 'LAST 30 DAYS' },
  { value: '90d', label: 'LAST 90 DAYS' },
  { value: '1y', label: 'LAST YEAR' },
  { value: 'all', label: 'ALL TIME' },
];

export function TimeRangeSelector({ selectedPeriod, onPeriodChange }: TimeRangeSelectorProps) {
  return (
    <div className="flex gap-2 font-mono">
      {PERIODS.map(({ value, label }) => (
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
          {label}
        </button>
      ))}
    </div>
  );
}
