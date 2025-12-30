import { Flame, CloudRain, Cloud, Sun, Zap, Coffee } from 'lucide-react';
import type { DashboardStats, RecentEntry } from '../../hooks/useDashboard';
import { ProgressBar } from '../ui/ProgressBar';
import { MoodSelector } from '../journal/MoodSelector';
import { useLanguage } from '../../contexts/LanguageContext';

interface RecentDay {
  hasEntry: boolean;
}

interface StatsPanelProps {
  stats: DashboardStats;
  recentEntries?: RecentEntry[];
  recentDays?: RecentDay[];
  onMoodSelect?: (mood: number) => void;
  selectedMood?: number | null;
}

/**
 * Get mood icon component based on mood rating
 */
function getMoodIcon(mood: number | null, size: number = 12) {
  const iconProps = { size, className: 'text-text-main' };

  switch (mood) {
    case 1:
      return <CloudRain {...iconProps} />;
    case 2:
      return <Cloud {...iconProps} />;
    case 3:
      return <Sun {...iconProps} />;
    case 4:
      return <Zap {...iconProps} />;
    case 5:
      return <Coffee {...iconProps} />;
    default:
      return null;
  }
}

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const day = date.getDate();
  const month = date.getMonth() + 1;
  return `${day}.${month}.`;
}

/**
 * Stats panel component for the dashboard context panel
 * Displays progress bar, streak badge, and mood selector
 */
export function StatsPanel({
  stats,
  recentEntries = [],
  recentDays = [],
  onMoodSelect,
  selectedMood
}: StatsPanelProps) {
  const { t } = useLanguage();

  // Generate default recentDays if not provided (last 7 days mock data)
  const displayRecentDays = recentDays.length > 0
    ? recentDays
    : Array.from({ length: 7 }).map((_, i) => ({ hasEntry: i >= 4 }));

  return (
    <div className="space-y-6">
      {/* Progress Section */}
      <div>
        <h3 className="text-xs font-bold uppercase mb-4 border-b-2 border-border pb-1 text-text-main">
          {t('meta.progress')}
        </h3>
        <ProgressBar
          value={stats.todayWords}
          max={stats.dailyGoal}
          showLabel={true}
          animated={true}
        />
      </div>

      {/* Streak Badge */}
      <div className="border-2 border-border p-3 bg-bg-panel shadow-hard">
        <div className="flex justify-between items-center mb-1">
          <span className="text-[10px] font-bold uppercase text-text-muted">
            {t('meta.currentStreak')}
          </span>
          <Flame size={14} className="text-text-main" />
        </div>
        <div className="text-3xl font-bold text-text-main">{stats.currentStreak}</div>
        {/* Mini bars for last 7 days */}
        <div className="flex gap-1 mt-2">
          {displayRecentDays.map((day, i) => (
            <div
              key={i}
              className={`h-1.5 flex-1 ${
                day.hasEntry
                  ? 'bg-accent'
                  : 'bg-bg-app border border-border opacity-30'
              }`}
            />
          ))}
        </div>
        <div className="mt-2 text-xs text-text-muted">
          <span>{t('dashboard.longestStreak') || 'Nejdelší'}: {stats.longestStreak}</span>
        </div>
      </div>

      {/* Mood Selector */}
      {onMoodSelect && (
        <div>
          <h3 className="text-xs font-bold uppercase mb-4 border-b-2 border-border pb-1 text-text-main">
            {t('meta.moodCheck')}
          </h3>
          <MoodSelector
            value={selectedMood as 1 | 2 | 3 | 4 | 5 | null}
            onChange={onMoodSelect}
          />
        </div>
      )}

      {/* Recent Days */}
      {recentEntries.length > 0 && (
        <div className="border-t-2 border-border pt-4">
          <h3 className="text-xs font-bold uppercase mb-2 text-text-main">
            {t('meta.recentDays')}
          </h3>
          <div className="space-y-2">
            {recentEntries.slice(0, 4).map((entry) => (
              <div
                key={entry.id}
                className="flex justify-between items-center text-xs border border-border py-4 px-2 hover:border-dashed cursor-pointer transition-all text-text-main"
              >
                <span className="font-bold">{formatDate(entry.created_at)}</span>
                <div className="flex items-center gap-2">
                  <span>{entry.word_count}</span>
                  {getMoodIcon(entry.mood_rating, 12)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
