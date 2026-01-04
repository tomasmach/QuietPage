import { Link } from 'react-router-dom';
import { Frown, Meh, Smile, Laugh, SmilePlus } from 'lucide-react';
import type { Entry } from '../../hooks/useEntries';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

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

  return (
    <Link to={`/entries/${entry.id}`} className="block group">
      <Card className="transition-all hover:translate-x-1 hover:translate-y-1 hover:border-dashed">
        <div className="space-y-3">
          {/* Header with date and mood */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-text-main uppercase">{formattedDate}</div>
              <div className="text-xs text-text-text-muted">{formattedTime}</div>
            </div>
            {MoodIcon && (
              <div className="flex-shrink-0">
                <MoodIcon className="h-5 w-5 text-text-muted" />
              </div>
            )}
          </div>

          {/* Title */}
          {entry.title && (
            <h3 className="font-bold text-lg text-text line-clamp-1 group-hover:text-accent">
              {entry.title}
            </h3>
          )}

          {/* Content preview */}
          {entry.content_preview && (
            <p className="text-text-muted text-sm line-clamp-3">{entry.content_preview}</p>
          )}

          {/* Footer with word count and tags */}
          <div className="flex items-center justify-between pt-2 border-t border-border">
            <div className="text-xs text-text-muted">{entry.word_count} slov</div>
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
