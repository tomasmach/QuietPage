import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useToast } from '@/contexts/ToastContext';
import { Logo } from '@/components/ui/Logo';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { LanguageToggle } from '@/components/ui/LanguageToggle';

export function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();
  const { t } = useLanguage();
  const toast = useToast();

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    try {
      await login(formData);
      navigate('/dashboard');
    } catch {
      toast.error(t('toast.loginError'));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative" style={{ backgroundColor: 'var(--color-bg-app)' }}>
      {/* Fixed toggles in corners */}
      <LanguageToggle />
      <ThemeToggle />

      {/* Login card */}
      <div className="w-full max-w-md">
        {/* Logo + Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size="md" />
          </div>
          <h1 className="text-3xl font-bold text-text-main font-mono uppercase tracking-wider">
            {t('auth.login')}
          </h1>
        </div>

        {/* Form Card */}
        <div className="bg-bg-panel border-2 border-border shadow-hard p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username/Email Input */}
            <Input
              label={t('auth.usernameOrEmail')}
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
              autoComplete="username"
              disabled={isLoading}
            />

            {/* Password Input */}
            <Input
              label={t('auth.password')}
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
              autoComplete="current-password"
              disabled={isLoading}
            />

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              className="w-full"
              loading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? t('auth.loggingIn') : t('auth.login')}
            </Button>

            {/* Links */}
            <div className="text-center space-y-3 text-sm font-mono pt-2">
              <p className="text-text-muted">
                {t('auth.noAccount')}{' '}
                <Link
                  to="/signup"
                  className="text-accent hover:underline font-bold uppercase tracking-wider"
                >
                  {t('auth.signup')}
                </Link>
              </p>
              <p>
                <Link
                  to="/"
                  className="text-text-muted hover:text-text-main uppercase tracking-wider"
                >
                  ← {t('auth.backToHome')}
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
