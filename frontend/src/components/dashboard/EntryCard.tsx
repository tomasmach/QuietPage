import { Link } from 'react-router-dom';
import { Frown, Meh, Smile, Laugh, SmilePlus } from 'lucide-react';
import type { Entry } from '../../hooks/useEntries';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { cn } from '../../lib/utils';

interface EntryCardProps {
  entry: Entry;
}

const MOOD_ICONS = {
  1: Frown,
  2: Meh,
  3: Smile,
  4: Laugh,
  5: SmilePlus,
};

/**
 * Card component for displaying an entry in the archive list
 */
export function EntryCard({ entry }: EntryCardProps) {
  const date = new Date(entry.created_at);
  const formattedDate = date.toLocaleDateString('cs-CZ', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  const formattedTime = date.toLocaleTimeString('cs-CZ', {
    hour: '2-digit',
    minute: '2-digit',
  });

  const MoodIcon = entry.mood_rating ? MOOD_ICONS[entry.mood_rating as keyof typeof MOOD_ICONS] : null;

  // Determine if entry is from today
  const entryDate = new Date(entry.created_at).toDateString();
  const todayDate = new Date().toDateString();
  const isToday = entryDate === todayDate;
  const linkTo = isToday ? '/write' : `/entries/${entry.id}`;

  return (
    <Link to={linkTo} className="block group">
      <Card className="transition-all hover:translate-x-1 hover:translate-y-1 hover:border-dashed">
        <div className="space-y-3">
          {/* Header with date and mood */}
          <div className="flex items-center justify-between">
            <div>
              <div className={cn("text-sm font-bold text-text-main uppercase theme-aware")}>{formattedDate}</div>
              <div className={cn("text-xs text-text-muted theme-aware")}>{formattedTime}</div>
            </div>
            {MoodIcon && (
              <div className="flex-shrink-0">
                <MoodIcon className={cn("h-5 w-5 text-text-muted theme-aware")} />
              </div>
            )}
          </div>

          {/* Title */}
          {entry.title && (
            <h3 className={cn("font-bold text-lg text-text line-clamp-1 group-hover:text-accent theme-aware")}>
              {entry.title}
            </h3>
          )}

          {/* Content preview */}
          {entry.content_preview && (
            <p className={cn("text-text-muted text-sm line-clamp-3 theme-aware")}>{entry.content_preview}</p>
          )}

          {/* Footer with word count and tags */}
          <div className={cn("flex items-center justify-between pt-2 border-t border-border theme-aware")}>
            <div className={cn("text-xs text-text-muted theme-aware")}>{entry.word_count} slov</div>
            {entry.tags.length > 0 && (
              <div className="flex gap-1 flex-wrap">
                {entry.tags.slice(0, 3).map((tag) => (
                  <Badge key={tag} className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {entry.tags.length > 3 && (
                  <Badge className="text-xs">
                    +{entry.tags.length - 3}
                  </Badge>
                )}
              </div>
            )}
          </div>
        </div>
      </Card>
    </Link>
  );
}
