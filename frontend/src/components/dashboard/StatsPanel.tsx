import type { DashboardStats } from '../../hooks/useDashboard';
import { ProgressBar } from '../ui/ProgressBar';
import { Badge } from '../ui/Badge';
import { MoodSelector } from '../journal/MoodSelector';
import { useLanguage } from '../../contexts/LanguageContext';

interface StatsPanelProps {
  stats: DashboardStats;
  onMoodSelect?: (mood: number) => void;
  selectedMood?: number | null;
}

/**
 * Stats panel component for the dashboard context panel
 * Displays progress bar, streak badge, and mood selector
 */
export function StatsPanel({ stats, onMoodSelect, selectedMood }: StatsPanelProps) {
  const { t } = useLanguage();

  const progressPercentage = Math.min(
    Math.round((stats.todayWords / stats.dailyGoal) * 100),
    100
  );

  return (
    <div className="space-y-6">
      {/* Progress Section */}
      <div>
        <h3 className="text-sm font-bold text-primary mb-2 uppercase tracking-wide">
          {t('meta.progress')}
        </h3>
        <div className="space-y-2">
          <div className="flex items-baseline justify-between text-sm">
            <span className="text-muted">{t('meta.wordsToday')}</span>
            <span className="font-bold text-text">
              {stats.todayWords} / {stats.dailyGoal}
            </span>
          </div>
          <ProgressBar value={progressPercentage} max={100} />
          {progressPercentage >= 100 && (
            <div className="text-xs text-accent font-medium">
              {t('meta.goalMet')} 🎉
            </div>
          )}
        </div>
      </div>

      {/* Streak Section */}
      <div>
        <h3 className="text-sm font-bold text-primary mb-2 uppercase tracking-wide">
          {t('meta.currentStreak')}
        </h3>
        <div className="flex items-center gap-3">
          <Badge className="text-base px-3 py-2">
            🔥 {stats.currentStreak}
          </Badge>
          <div className="text-xs text-muted">
            <div>Nejdelší: {stats.longestStreak}</div>
            <div>Celkem: {stats.totalEntries} záznamů</div>
          </div>
        </div>
      </div>

      {/* Mood Selector */}
      {onMoodSelect && (
        <div>
          <h3 className="text-sm font-bold text-primary mb-2 uppercase tracking-wide">
            {t('meta.moodCheck')}
          </h3>
          <MoodSelector
            value={selectedMood as 1 | 2 | 3 | 4 | 5 | null}
            onChange={onMoodSelect}
          />
        </div>
      )}

      {/* Recent Days Mini Calendar */}
      <div>
        <h3 className="text-sm font-bold text-primary mb-2 uppercase tracking-wide">
          {t('meta.recentDays')}
        </h3>
        <div className="grid grid-cols-7 gap-1">
          {Array.from({ length: 7 }).map((_, i) => {
            const date = new Date();
            date.setDate(date.getDate() - (6 - i));
            const dayName = date.toLocaleDateString('cs-CZ', { weekday: 'short' });

            // This would need real data from the backend
            const hasEntry = i >= 4; // Mock data

            return (
              <div
                key={i}
                className="aspect-square flex flex-col items-center justify-center border-2 border-border"
              >
                <div className="text-xs text-muted">{dayName}</div>
                <div className="text-lg">{hasEntry ? '✓' : '·'}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
