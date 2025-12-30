import { Link } from 'react-router-dom';
import type { Entry } from '../../hooks/useEntries';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface EntryCardProps {
  entry: Entry;
}

const MOOD_EMOJIS: Record<number, string> = {
  1: '😢',
  2: '😕',
  3: '😐',
  4: '🙂',
  5: '😄',
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

  return (
    <Link to={`/entries/${entry.id}`} className="block group">
      <Card className="transition-all hover:translate-x-1 hover:translate-y-1 hover:border-dashed">
        <div className="space-y-3">
          {/* Header with date and mood */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-text-main uppercase">{formattedDate}</div>
              <div className="text-xs text-text-muted">{formattedTime}</div>
            </div>
            {entry.mood_rating && (
              <div className="text-2xl">{MOOD_EMOJIS[entry.mood_rating]}</div>
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
            <p className="text-muted text-sm line-clamp-3">{entry.content_preview}</p>
          )}

          {/* Footer with word count and tags */}
          <div className="flex items-center justify-between pt-2 border-t border-border">
            <div className="text-xs text-muted">{entry.word_count} slov</div>
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
