import { cn } from '@/lib/utils';
import { CloudRain, Cloud, Sun, Zap, Coffee } from 'lucide-react';

export interface MoodSelectorProps {
  value: 1 | 2 | 3 | 4 | 5 | null;
  onChange: (mood: 1 | 2 | 3 | 4 | 5) => void;
  disabled?: boolean;
}

const moods = [
  { value: 1 as const, icon: CloudRain, label: 'Very Bad' },
  { value: 2 as const, icon: Cloud, label: 'Bad' },
  { value: 3 as const, icon: Sun, label: 'Neutral' },
  { value: 4 as const, icon: Zap, label: 'Good' },
  { value: 5 as const, icon: Coffee, label: 'Excellent' },
];

export function MoodSelector({ value, onChange, disabled = false }: MoodSelectorProps) {
  return (
    <div className="w-full">
      <div className="flex gap-2 justify-between" role="radiogroup" aria-label="Select mood">
        {moods.map(({ value: moodValue, icon: Icon, label }) => {
          const isSelected = value === moodValue;
          return (
            <button
              key={moodValue}
              type="button"
              onClick={() => onChange(moodValue)}
              disabled={disabled}
              className={cn(
                'flex-1 aspect-square border-2 border-border flex items-center justify-center',
                'transition-colors duration-150',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                isSelected
                  ? 'bg-accent text-accent-fg shadow-hard'
                  : 'bg-bg-panel text-text-main hover:bg-bg-app'
              )}
              role="radio"
              aria-checked={isSelected}
              aria-label={label}
            >
              <Icon className="h-5 w-5" />
            </button>
          );
        })}
      </div>
    </div>
  );
}
