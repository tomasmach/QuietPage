import { useState, type FormEvent } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useSettings } from '@/hooks/useSettings';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { AlertTriangle } from 'lucide-react';

const CONFIRMATION_TEXT = 'SMAZAT';

export function DeleteAccountPage() {
  const { t, language } = useLanguage();
  const { isLoading, error, clearMessages, deleteAccount } = useSettings();

  const [formData, setFormData] = useState({
    password: '',
    confirmation_text: '',
  });

  const confirmationWord = language === 'cs' ? CONFIRMATION_TEXT : 'DELETE';
  const isConfirmationValid = formData.confirmation_text === confirmationWord;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearMessages();

    if (!isConfirmationValid) {
      return;
    }

    await deleteAccount({
      password: formData.password,
      confirmation_text: formData.confirmation_text,
    });
  };

  return (
    <Card className="border-red-500">
      {/* Warning Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-red-100 dark:bg-red-950/50 border-2 border-red-500">
          <AlertTriangle className="w-6 h-6 text-red-600" />
        </div>
        <h2 className="text-2xl font-bold text-red-600 font-mono uppercase tracking-wider">
          {t('settings.delete.title')}
        </h2>
      </div>

      {/* Warning Message */}
      <div className="p-4 mb-6 border-2 border-red-500 bg-red-50 dark:bg-red-950/30">
        <p className="text-red-700 dark:text-red-400 text-sm font-mono font-bold mb-2">
          {t('settings.delete.warning')}
        </p>
        <ul className="text-red-600 dark:text-red-400 text-sm font-mono list-disc list-inside space-y-1">
          <li>{t('settings.delete.warningItem1')}</li>
          <li>{t('settings.delete.warningItem2')}</li>
          <li>{t('settings.delete.warningItem3')}</li>
        </ul>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Password */}
        <Input
          label={t('settings.delete.password')}
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          disabled={isLoading}
          required
          autoComplete="current-password"
        />

        {/* Confirmation Text */}
        <Input
          label={t('settings.delete.confirmationLabel')}
          type="text"
          value={formData.confirmation_text}
          onChange={(e) =>
            setFormData({ ...formData, confirmation_text: e.target.value.toUpperCase() })
          }
          disabled={isLoading}
          required
          helperText={t('settings.delete.confirmationHint', { word: confirmationWord })}
          error={
            formData.confirmation_text && !isConfirmationValid
              ? t('settings.delete.confirmationError', { word: confirmationWord })
              : undefined
          }
        />

        {/* Error Message */}
        {error && (
          <div className="p-4 border-2 border-red-500 bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-400 text-sm font-mono font-bold">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end">
          <Button
            type="submit"
            variant="danger"
            loading={isLoading}
            disabled={isLoading || !isConfirmationValid || !formData.password}
          >
            {t('settings.delete.deleteButton')}
          </Button>
        </div>
      </form>
    </Card>
  );
}
