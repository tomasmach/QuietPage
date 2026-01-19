import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { Card } from '../components/ui/Card';
import { SEO } from '../components/SEO';
import { EntryCard } from '../components/dashboard/EntryCard';
import { useEntries } from '../hooks/useEntries';
import { useLanguage } from '../contexts/LanguageContext';

export function ArchivePage() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const { entries, isLoading, error, page, setPage, hasMore, totalCount } = useEntries(20);

  const handleNewEntry = () => {
    navigate('/entries/new');
  };

  const handlePreviousPage = () => {
    if (page > 1) {
      setPage(page - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleNextPage = () => {
    if (hasMore) {
      setPage(page + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <>
      <SEO
        title="Archive"
        description="Browse your journal archive - explore all your past entries and reflections."
      />
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8 border-b-2 border-border pb-4 border-dashed">
            <div>
              <div className="text-xs font-bold uppercase text-text-muted mb-1">
                {t('nav.archive')}
              </div>
              <h1 className="text-3xl font-bold uppercase text-text-main">
                {t('archive.totalEntries', { count: totalCount })}
              </h1>
            </div>
            <Button onClick={handleNewEntry}>{t('dashboard.newEntry')}</Button>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Spinner size="lg" />
            </div>
          )}

          {/* Error State */}
          {error && !isLoading && (
            <Card>
              <p className="text-error">
                {t('archive.errorLoading')}
              </p>
            </Card>
          )}

          {/* Empty State */}
          {!isLoading && !error && entries.length === 0 && (
            <Card className="text-center py-12">
              <p className="text-text-muted mb-4">{t('dashboard.noEntries')}</p>
              <Button onClick={handleNewEntry}>{t('dashboard.newEntry')}</Button>
            </Card>
          )}

          {/* Entries Grid */}
          {!isLoading && !error && entries.length > 0 && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {entries.map((entry) => (
                  <EntryCard key={entry.id} entry={entry} />
                ))}
              </div>

              {/* Pagination */}
              {(page > 1 || hasMore) && (
                <div className="flex items-center justify-center gap-4 mt-8">
                  <Button
                    onClick={handlePreviousPage}
                    disabled={page === 1}
                    variant="secondary"
                  >
                    {t('archive.previous')}
                  </Button>
                  <span className="text-text-muted">
                    {t('archive.page', { page })}
                  </span>
                  <Button
                    onClick={handleNextPage}
                    disabled={!hasMore}
                    variant="secondary"
                  >
                    {t('archive.next')}
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
        <ThemeToggle />
      </AppLayout>
    </>
  );
}
