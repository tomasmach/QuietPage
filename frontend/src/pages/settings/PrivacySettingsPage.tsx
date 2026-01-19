import { useState, type FormEvent } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useSettings } from '@/hooks/useSettings';
import { useToast } from '@/contexts/ToastContext';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { SEO } from '@/components/SEO';

export function PrivacySettingsPage() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const { isLoading, clearMessages, updatePrivacy } = useSettings();
  const toast = useToast();

  const [formData, setFormData] = useState({
    email_notifications: user?.email_notifications ?? true,
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearMessages();
    const result = await updatePrivacy(formData);
    if (result) {
      toast.success(t('toast.privacyUpdated'));
    } else {
      toast.error(t('toast.saveError'));
    }
  };

  return (
    <>
      <SEO title="Privacy Settings" description="Control your privacy and data settings." />
      <Card>
        <h2 className="text-2xl font-bold text-text-main mb-6 font-mono uppercase tracking-wider">
          {t('settings.privacy.title')}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email Notifications */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-text-main font-mono uppercase tracking-wider">
            {t('settings.privacy.notifications')}
          </h3>

          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="email_notifications"
              checked={formData.email_notifications}
              onChange={(e) =>
                setFormData({ ...formData, email_notifications: e.target.checked })
              }
              disabled={isLoading}
              className="w-5 h-5 mt-0.5 border-2 border-border bg-bg-panel accent-accent cursor-pointer"
            />
            <div>
              <label
                htmlFor="email_notifications"
                className="text-sm font-mono text-text-main cursor-pointer font-bold"
              >
                {t('settings.privacy.emailNotifications')}
              </label>
              <p className="text-xs text-text-muted font-mono mt-1">
                {t('settings.privacy.emailNotificationsHint')}
              </p>
            </div>
          </div>
        </div>

        {/* Privacy Info */}
        <div className="border-t-2 border-border pt-6 mt-6">
          <h3 className="text-lg font-bold text-text-main mb-4 font-mono uppercase tracking-wider">
            {t('settings.privacy.dataPrivacy')}
          </h3>
          <div className="space-y-3 text-sm font-mono text-text-muted">
            <p>{t('settings.privacy.encryptionInfo')}</p>
            <p>{t('settings.privacy.dataUsageInfo')}</p>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <Button type="submit" variant="primary" loading={isLoading} disabled={isLoading}>
            {t('common.save')}
          </Button>
        </div>
      </form>
      </Card>
    </>
  );
}
