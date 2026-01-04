import { Link } from 'react-router-dom';
import { Frown, Meh, Smile, Laugh, SmilePlus } from 'lucide-react';
import type { RecentEntry } from '../../hooks/useDashboard';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { useLanguage } from '../../contexts/LanguageContext';

interface RecentEntriesProps {
  entries: RecentEntry[];
  onNewEntry: () => void;
}

const MOOD_ICONS = {
  1: Frown,
  2: Meh,
  3: Smile,
  4: Laugh,
  5: SmilePlus,
};

/**
 * Component for displaying recent entries on the dashboard
 */
export function RecentEntries({ entries, onNewEntry }: RecentEntriesProps) {
  const { t } = useLanguage();

  if (entries.length === 0) {
    return (
      <Card className="text-center py-12">
        <p className="text-text-muted mb-4">{t('dashboard.noEntries')}</p>
        <Button onClick={onNewEntry}>{t('dashboard.newEntry')}</Button>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-accent">{t('dashboard.recentEntries')}</h2>
        <Button onClick={onNewEntry} size="sm">
          {t('dashboard.newEntry')}
        </Button>
      </div>

      <div className="space-y-3">
        {entries.map((entry) => {
          const date = new Date(entry.created_at);
          const formattedDate = date.toLocaleDateString('cs-CZ', {
            day: 'numeric',
            month: 'short',
          });

          const formattedTime = date.toLocaleTimeString('cs-CZ', {
            hour: '2-digit',
            minute: '2-digit',
          });

          const MoodIcon = entry.mood_rating ? MOOD_ICONS[entry.mood_rating as keyof typeof MOOD_ICONS] : null;

          return (
            <Link key={entry.id} to={`/entries/${entry.id}`} className="block group">
              <Card className="transition-transform hover:translate-x-1 hover:translate-y-1">
                <div className="flex items-start gap-3 justify-between">
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline gap-2 mb-1">
                      <span className="text-xs font-bold text-accent">
                        {formattedDate}
                      </span>
                      <span className="text-xs text-text-muted">{formattedTime}</span>
                    </div>

                    {entry.title && (
                      <h3 className="font-bold text-text group-hover:text-accent line-clamp-1 mb-1">
                        {entry.title}
                      </h3>
                    )}

                    <p className="text-sm text-text-muted line-clamp-2">
                      {entry.content_preview}
                    </p>

                    <div className="text-xs text-text-muted mt-2">{entry.word_count} slov</div>
                  </div>

                  {/* Mood indicator */}
                  {MoodIcon && (
                    <div className="flex-shrink-0">
                      <MoodIcon className="h-5 w-5 text-text-muted" />
                    </div>
                  )}
                </div>
              </Card>
            </Link>
          );
        })}
      </div>

      <div className="text-center pt-2">
        <Link
          to="/archive"
          className="text-sm text-accent hover:underline font-medium"
        >
          {t('dashboard.viewAll')} →
        </Link>
      </div>
    </div>
  );
}
