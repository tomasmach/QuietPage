import { Link } from 'react-router-dom';
import { History, RefreshCw } from 'lucide-react';
import type { FeaturedEntry as FeaturedEntryType } from '../../hooks/useDashboard';
import { Card } from '../ui/Card';
import { useLanguage } from '../../contexts/LanguageContext';
import { cn } from '../../lib/utils';

interface FeaturedEntryProps {
  entry: FeaturedEntryType | null;
  onRefresh: () => void;
  isRefreshing: boolean;
}

/**
 * FeaturedEntry component displays a random historical entry from the user's journal
 * with a "Show another" refresh button.
 */
export function FeaturedEntry({ entry, onRefresh, isRefreshing }: FeaturedEntryProps) {
  const { t } = useLanguage();

  // Don't render anything if there's no entry
  if (!entry) {
    return null;
  }

  const formattedDate = new Date(entry.created_at).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  return (
    <Card className="space-y-4">
      {/* Header with icon and title */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'flex items-center justify-center w-8 h-8 border-2 border-border theme-aware'
            )}
          >
            <History size={16} className={cn('text-text-main theme-aware')} />
          </div>
          <h3
            className={cn(
              'text-sm font-bold uppercase tracking-wide text-text-main theme-aware'
            )}
          >
            {t('dashboard.featuredEntry.title')}
          </h3>
        </div>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 border-2 border-border',
            'text-sm font-medium uppercase tracking-wide',
            'hover:bg-accent hover:text-accent-fg',
            'transition-all duration-150 theme-aware',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          <RefreshCw
            size={14}
            className={cn(isRefreshing && 'animate-spin')}
          />
          <span className="hidden sm:inline">
            {isRefreshing
              ? t('dashboard.featuredEntry.refreshing')
              : t('dashboard.featuredEntry.refresh')}
          </span>
        </button>
      </div>

      {/* Entry content */}
      <Link to={`/entries/${entry.id}`} className="block group">
        <div className="space-y-2">
          {/* Entry title */}
          {entry.title && (
            <h4
              className={cn(
                'font-bold text-lg text-text-main group-hover:text-accent line-clamp-1 theme-aware'
              )}
            >
              {entry.title}
            </h4>
          )}

          {/* Content preview */}
          <p
            className={cn(
              'text-text-muted line-clamp-3 leading-relaxed theme-aware'
            )}
          >
            {entry.content_preview}
          </p>

          {/* Meta info: date and word count */}
          <div className="flex items-center gap-4 pt-2">
            <span className={cn('text-xs text-text-muted theme-aware')}>
              {formattedDate}
            </span>
            <span className={cn('text-xs text-text-muted theme-aware')}>
              {t('dashboard.featuredEntry.daysAgo', { count: entry.days_ago })}
            </span>
            <span className={cn('text-xs text-text-muted theme-aware')}>
              {entry.word_count} {t('meta.wordsSuffix')}
            </span>
          </div>
        </div>
      </Link>
    </Card>
  );
}
