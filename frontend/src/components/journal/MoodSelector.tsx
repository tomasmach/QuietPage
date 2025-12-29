import { cn } from '@/lib/utils';
import { CloudRain, Cloud, Meh, Sun, Zap } from 'lucide-react';

export interface MoodSelectorProps {
  value: 1 | 2 | 3 | 4 | 5 | null;
  onChange: (mood: 1 | 2 | 3 | 4 | 5) => void;
  disabled?: boolean;
}

const moods = [
  { value: 1 as const, icon: CloudRain, label: 'Very Bad' },
  { value: 2 as const, icon: Cloud, label: 'Bad' },
  { value: 3 as const, icon: Meh, label: 'Neutral' },
  { value: 4 as const, icon: Sun, label: 'Good' },
  { value: 5 as const, icon: Zap, label: 'Excellent' },
];

export function MoodSelector({ value, onChange, disabled = false }: MoodSelectorProps) {
  return (
    <div className="w-full">
      <label className="block mb-2 text-xs font-bold uppercase tracking-wider text-text-muted font-mono">
        Mood
      </label>
      <div className="grid grid-cols-5 gap-2" role="radiogroup" aria-label="Select mood">
        {moods.map(({ value: moodValue, icon: Icon, label }) => {
          const isSelected = value === moodValue;
          return (
            <button
              key={moodValue}
              type="button"
              onClick={() => onChange(moodValue)}
              disabled={disabled}
              className={cn(
                'aspect-square border-2 border-border flex items-center justify-center',
                'transition-all duration-150',
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
