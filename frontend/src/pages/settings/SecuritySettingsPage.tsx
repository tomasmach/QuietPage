import { useState, type FormEvent } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useSettings } from '@/hooks/useSettings';
import { useToast } from '@/contexts/ToastContext';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export function SecuritySettingsPage() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const {
    isLoading,
    clearMessages,
    changePassword,
    changeEmail,
  } = useSettings();
  const toast = useToast();

  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    new_password_confirm: '',
  });

  // Email form state
  const [emailForm, setEmailForm] = useState({
    new_email: '',
    password: '',
  });

  // Track which form was submitted
  const [activeForm, setActiveForm] = useState<'password' | 'email' | null>(null);

  const handlePasswordSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearMessages();
    setActiveForm('password');

    // Validate passwords match
    if (passwordForm.new_password !== passwordForm.new_password_confirm) {
      return;
    }

    const result = await changePassword(passwordForm);
    if (result) {
      setPasswordForm({
        current_password: '',
        new_password: '',
        new_password_confirm: '',
      });
      toast.success(t('toast.passwordChanged'));
    } else {
      toast.error(t('toast.saveError'));
    }
  };

  const handleEmailSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearMessages();
    setActiveForm('email');

    const result = await changeEmail(emailForm);
    if (result) {
      setEmailForm({
        new_email: '',
        password: '',
      });
      toast.success(t('toast.emailChanged'));
    } else {
      toast.error(t('toast.saveError'));
    }
  };

  const passwordsMatch = passwordForm.new_password === passwordForm.new_password_confirm;
  const passwordError = passwordForm.new_password && passwordForm.new_password_confirm && !passwordsMatch
    ? t('settings.security.passwordsDoNotMatch')
    : undefined;

  return (
    <div className="space-y-6">
      {/* Change Password Section */}
      <Card>
        <h2 className="text-2xl font-bold text-text-main mb-6 font-mono uppercase tracking-wider">
          {t('settings.security.changePassword')}
        </h2>

        <form onSubmit={handlePasswordSubmit} className="space-y-6">
          <Input
            label={t('settings.security.currentPassword')}
            type="password"
            value={passwordForm.current_password}
            onChange={(e) =>
              setPasswordForm({ ...passwordForm, current_password: e.target.value })
            }
            disabled={isLoading}
            required
            autoComplete="current-password"
          />

          <Input
            label={t('settings.security.newPassword')}
            type="password"
            value={passwordForm.new_password}
            onChange={(e) =>
              setPasswordForm({ ...passwordForm, new_password: e.target.value })
            }
            disabled={isLoading}
            required
            autoComplete="new-password"
            helperText={t('settings.security.passwordHint')}
          />

          <Input
            label={t('settings.security.confirmNewPassword')}
            type="password"
            value={passwordForm.new_password_confirm}
            onChange={(e) =>
              setPasswordForm({ ...passwordForm, new_password_confirm: e.target.value })
            }
            disabled={isLoading}
            required
            autoComplete="new-password"
            error={passwordError}
          />

          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              loading={isLoading && activeForm === 'password'}
              disabled={isLoading || !passwordsMatch}
            >
              {t('settings.security.updatePassword')}
            </Button>
          </div>
        </form>
      </Card>

      {/* Change Email Section */}
      <Card>
        <h2 className="text-2xl font-bold text-text-main mb-6 font-mono uppercase tracking-wider">
          {t('settings.security.changeEmail')}
        </h2>

        <p className="text-sm text-text-muted font-mono mb-4">
          {t('settings.security.currentEmail')}: <span className="text-text-main font-bold">{user?.email}</span>
        </p>

        <form onSubmit={handleEmailSubmit} className="space-y-6">
          <Input
            label={t('settings.security.newEmail')}
            type="email"
            value={emailForm.new_email}
            onChange={(e) => setEmailForm({ ...emailForm, new_email: e.target.value })}
            disabled={isLoading}
            required
            autoComplete="email"
          />

          <Input
            label={t('settings.security.passwordForEmail')}
            type="password"
            value={emailForm.password}
            onChange={(e) => setEmailForm({ ...emailForm, password: e.target.value })}
            disabled={isLoading}
            required
            autoComplete="current-password"
            helperText={t('settings.security.passwordForEmailHint')}
          />

          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              loading={isLoading && activeForm === 'email'}
              disabled={isLoading}
            >
              {t('settings.security.updateEmail')}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
