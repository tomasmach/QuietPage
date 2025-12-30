import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { Logo } from '@/components/ui/Logo';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { LanguageToggle } from '@/components/ui/LanguageToggle';

export function SignupPage() {
  const navigate = useNavigate();
  const { register, isLoading } = useAuth();
  const { t } = useLanguage();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
  });
  const [errors, setErrors] = useState<{
    general?: string;
    username?: string;
    email?: string;
    password?: string;
    password_confirm?: string;
  }>({});

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      await register(formData);
      navigate('/dashboard');
    } catch (err: unknown) {
      // Handle different error formats
      if (err instanceof Error) {
        try {
          // Try to parse JSON error response
          const errorData = JSON.parse(err.message);
          if (typeof errorData === 'object') {
            setErrors(errorData);
          } else {
            setErrors({ general: t('auth.signupError') });
          }
        } catch {
          // If not JSON, treat as general error
          setErrors({ general: err.message || t('auth.signupError') });
        }
      } else {
        setErrors({ general: t('auth.signupError') });
      }
    }
  };

  return (
    <div className="min-h-screen bg-bg-main flex items-center justify-center p-4 relative">
      {/* Fixed toggles in corners */}
      <LanguageToggle />
      <ThemeToggle />

      {/* Signup card */}
      <div className="w-full max-w-md">
        {/* Logo + Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size="md" />
          </div>
          <h1 className="text-3xl font-bold text-text-main font-mono uppercase tracking-wider">
            {t('auth.register')}
          </h1>
        </div>

        {/* Form Card */}
        <div className="bg-bg-panel border-2 border-border shadow-hard p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username Input */}
            <Input
              label={t('auth.username')}
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
              autoComplete="username"
              disabled={isLoading}
              error={errors.username}
            />

            {/* Email Input */}
            <Input
              label={t('auth.email')}
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              autoComplete="email"
              disabled={isLoading}
              error={errors.email}
            />

            {/* Password Input */}
            <Input
              label={t('auth.password')}
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
              autoComplete="new-password"
              disabled={isLoading}
              error={errors.password}
            />

            {/* Password Confirm Input */}
            <Input
              label={t('auth.passwordConfirm')}
              type="password"
              value={formData.password_confirm}
              onChange={(e) => setFormData({ ...formData, password_confirm: e.target.value })}
              required
              autoComplete="new-password"
              disabled={isLoading}
              error={errors.password_confirm}
            />

            {/* General Error Message */}
            {errors.general && (
              <div className="p-4 border-2 border-red-500 bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-400 text-sm font-mono font-bold">
                {errors.general}
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              className="w-full"
              loading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? t('auth.signingUp') : t('auth.createAccount')}
            </Button>

            {/* Links */}
            <div className="text-center space-y-3 text-sm font-mono pt-2">
              <p className="text-text-muted">
                {t('auth.hasAccount')}{' '}
                <Link
                  to="/login"
                  className="text-accent hover:underline font-bold uppercase tracking-wider"
                >
                  {t('auth.login')}
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
