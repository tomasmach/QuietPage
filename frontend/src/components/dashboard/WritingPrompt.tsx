import { Lightbulb, ArrowRight } from 'lucide-react';
import { Card } from '../ui/Card';
import { useLanguage } from '../../contexts/LanguageContext';
import { translations } from '../../locales';
import { cn } from '../../lib/utils';

interface WritingPromptProps {
  onStartWriting: () => void;
}

/**
 * Get the day of year (1-366)
 */
function getDayOfYear(): number {
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 0);
  const diff = now.getTime() - start.getTime();
  const oneDay = 1000 * 60 * 60 * 24;
  return Math.floor(diff / oneDay);
}

/**
 * WritingPrompt component displays a daily writing prompt that rotates based on the day of year.
 * Includes a CTA button to start writing.
 */
export function WritingPrompt({ onStartWriting }: WritingPromptProps) {
  const { t, language } = useLanguage();

  // Get prompts array from translations
  const prompts = translations[language].dashboard.prompts;

  // Select prompt based on day of year
  const dayOfYear = getDayOfYear();
  const promptIndex = dayOfYear % prompts.length;
  const todayPrompt = prompts[promptIndex];

  return (
    <Card className="space-y-4">
      {/* Header with icon and title */}
      <div className="flex items-center gap-3">
        <div
          className={cn(
            'flex items-center justify-center w-8 h-8 border-2 border-border theme-aware'
          )}
        >
          <Lightbulb size={16} className={cn('text-text-main theme-aware')} />
        </div>
        <h3
          className={cn(
            'text-sm font-bold uppercase tracking-wide text-text-main theme-aware'
          )}
        >
          {t('dashboard.writingPrompt.title')}
        </h3>
      </div>

      {/* Prompt text */}
      <p
        className={cn(
          'text-lg leading-relaxed text-text-main theme-aware'
        )}
      >
        {todayPrompt}
      </p>

      {/* CTA Button */}
      <button
        onClick={onStartWriting}
        className={cn(
          'flex items-center gap-2 px-4 py-2 border-2 border-border',
          'bg-accent text-accent-fg font-bold text-sm uppercase tracking-wide',
          'shadow-hard hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none',
          'transition-all duration-150 theme-aware'
        )}
      >
        {t('dashboard.writingPrompt.cta')}
        <ArrowRight size={16} />
      </button>
    </Card>
  );
}
