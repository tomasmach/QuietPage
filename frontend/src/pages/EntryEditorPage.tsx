import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { ContextPanel } from '../components/layout/ContextPanel';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { Card } from '../components/ui/Card';
import { Modal } from '../components/ui/Modal';
import { MoodSelector } from '../components/journal/MoodSelector';
import { TagInput } from '../components/journal/TagInput';
import { WordCount } from '../components/journal/WordCount';
import { useEntry } from '../hooks/useEntry';
import { useAutoSave } from '../hooks/useAutoSave';
import { useLanguage } from '../contexts/LanguageContext';

export function EntryEditorPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useLanguage();

  const { entry, isLoading, error, save, remove } = useEntry(id);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [moodRating, setMoodRating] = useState<number | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Auto-save functionality
  const { save: autoSave, isSaving: isAutoSaving, lastSaved } = useAutoSave(id, {
    onSuccess: (newId) => {
      // If creating a new entry, navigate to the edit page
      if (!id && newId) {
        navigate(`/entries/${newId}`, { replace: true });
      }
    },
  });

  // Initialize form from entry data
  useEffect(() => {
    if (entry) {
      setTitle(entry.title || '');
      setContent(entry.content);
      setMoodRating(entry.mood_rating);
      setTags(entry.tags);
    }
  }, [entry]);

  // Auto-save when content changes
  useEffect(() => {
    if (content || title) {
      autoSave({
        title: title || undefined,
        content,
        mood_rating: moodRating,
        tags,
      });
    }
  }, [title, content, moodRating, tags]);

  // Word count
  const wordCount = content.trim().split(/\s+/).filter(Boolean).length;

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await save({
        title: title || undefined,
        content,
        mood_rating: moodRating,
        tags,
      });
      navigate('/dashboard');
    } catch (err) {
      // Error is handled by the hook
      console.error('Failed to save entry:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    try {
      await remove();
      navigate('/dashboard');
    } catch (err) {
      // Error is handled by the hook
      console.error('Failed to delete entry:', err);
    }
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  if (isLoading && id) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8 flex items-center justify-center min-h-[50vh]">
          <Spinner size="lg" />
        </div>
        <ThemeToggle />
      </AppLayout>
    );
  }

  if (error && id) {
    return (
      <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
        <div className="p-8">
          <Card>
            <p className="text-error">
              Chyba při načítání záznamu: {error.message}
            </p>
            <Button onClick={handleCancel} className="mt-4">
              {t('common.cancel')}
            </Button>
          </Card>
        </div>
        <ThemeToggle />
      </AppLayout>
    );
  }

  const date = entry
    ? new Date(entry.created_at)
    : new Date();

  const formattedDate = date.toLocaleDateString('cs-CZ', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return (
    <AppLayout
      sidebar={<Sidebar />}
      contextPanel={
        <ContextPanel>
          <div className="space-y-6">
            {/* Mood Selector */}
            <div>
              <h3 className="text-sm font-bold text-primary mb-2 uppercase tracking-wide">
                {t('meta.moodCheck')}
              </h3>
              <MoodSelector
                value={moodRating as 1 | 2 | 3 | 4 | 5 | null}
                onChange={setMoodRating}
              />
            </div>

            {/* Tags */}
            <div>
              <h3 className="text-sm font-bold text-primary mb-2 uppercase tracking-wide">
                {t('entry.tags')}
              </h3>
              <TagInput value={tags} onChange={setTags} />
            </div>

            {/* Actions */}
            <div className="space-y-3">
              <Button
                onClick={handleSave}
                disabled={isSaving || !content}
                className="w-full"
              >
                {isSaving ? t('entry.saving') : t('common.save')}
              </Button>

              <Button onClick={handleCancel} variant="secondary" className="w-full">
                {t('common.cancel')}
              </Button>

              {id && (
                <Button
                  onClick={() => setShowDeleteModal(true)}
                  variant="danger"
                  className="w-full"
                >
                  {t('common.delete')}
                </Button>
              )}
            </div>

            {/* Auto-save indicator */}
            {isAutoSaving && (
              <p className="text-xs text-muted">{t('entry.saving')}...</p>
            )}
            {lastSaved && !isAutoSaving && (
              <p className="text-xs text-muted">
                {t('entry.saved')}{' '}
                {lastSaved.toLocaleTimeString('cs-CZ', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            )}
          </div>
        </ContextPanel>
      }
    >
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-4xl font-bold text-primary">
              {id ? t('entry.editEntry') : t('entry.newEntry')}
            </h1>
            <WordCount current={wordCount} />
          </div>
          <p className="text-muted">{formattedDate}</p>
        </div>

        {/* Editor */}
        <div className="space-y-4">
          {/* Title */}
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={t('entry.titlePlaceholder')}
            className="text-2xl font-bold"
          />

          {/* Content */}
          <Textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={t('entry.contentPlaceholder')}
            rows={20}
            className="text-lg resize-none"
            autoFocus={!id}
          />
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title={t('entry.deleteTitle')}
      >
        <div className="space-y-4">
          <p className="text-text">{t('entry.confirmDelete')}</p>
          <div className="flex gap-3">
            <Button onClick={handleDelete} variant="danger">
              {t('common.delete')}
            </Button>
            <Button onClick={() => setShowDeleteModal(false)} variant="secondary">
              {t('common.cancel')}
            </Button>
          </div>
        </div>
      </Modal>

      <ThemeToggle />
    </AppLayout>
  );
}
