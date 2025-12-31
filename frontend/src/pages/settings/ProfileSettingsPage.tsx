import { useState, useRef, type FormEvent, type ChangeEvent } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useTheme } from '@/contexts/ThemeContext';
import { useSettings } from '@/hooks/useSettings';
import { useToast } from '@/contexts/ToastContext';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import { Avatar } from '@/components/ui/Avatar';
import { Upload, Moon, Sun } from 'lucide-react';

export function ProfileSettingsPage() {
  const { user } = useAuth();
  const { t, language, setLanguage } = useLanguage();
  const { theme, setTheme } = useTheme();
  const { isLoading, clearMessages, updateProfile, uploadAvatar } = useSettings();
  const toast = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    bio: user?.bio || '',
  });
  const [avatarPreview, setAvatarPreview] = useState<string | null>(user?.avatar || null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearMessages();
    const result = await updateProfile({
      first_name: formData.first_name,
      last_name: formData.last_name,
      bio: formData.bio,
    });
    if (result) {
      toast.success(t('toast.profileUpdated'));
    } else {
      toast.error(t('toast.saveError'));
    }
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (event) => {
      setAvatarPreview(event.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Upload avatar
    const result = await uploadAvatar(file);
    if (result) {
      toast.success(t('toast.avatarUploaded'));
    }
  };

  return (
    <>
    <Card>
      <h2 className="text-2xl font-bold text-text-main mb-6 font-mono uppercase tracking-wider">
        {t('settings.profile.title')}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Avatar Section */}
        <div className="flex items-center gap-6">
          <div className="relative group cursor-pointer" onClick={handleAvatarClick}>
            <Avatar
              src={avatarPreview || undefined}
              alt={user?.username || 'User'}
              size="lg"
              fallback={user?.username}
              className="w-24 h-24"
            />
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <Upload className="w-6 h-6 text-white" />
            </div>
          </div>
          <div>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={handleAvatarClick}
              disabled={isLoading}
            >
              {t('settings.profile.uploadAvatar')}
            </Button>
            <p className="text-xs text-text-muted mt-2 font-mono">
              {t('settings.profile.avatarHint')}
            </p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleAvatarChange}
            className="hidden"
          />
        </div>

        {/* Name Fields */}
        <div className="grid grid-cols-2 gap-4">
          <Input
            label={t('settings.profile.firstName')}
            value={formData.first_name}
            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
            disabled={isLoading}
          />
          <Input
            label={t('settings.profile.lastName')}
            value={formData.last_name}
            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
            disabled={isLoading}
          />
        </div>

        {/* Bio */}
        <Textarea
          label={t('settings.profile.bio')}
          value={formData.bio}
          onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
          rows={4}
          disabled={isLoading}
          helperText={t('settings.profile.bioHint')}
        />

        {/* Submit Button */}
        <div className="flex justify-end">
          <Button type="submit" variant="primary" loading={isLoading} disabled={isLoading}>
            {t('common.save')}
          </Button>
        </div>
      </form>
    </Card>

    {/* Appearance Section */}
    <Card className="mt-6">
      <h2 className="text-2xl font-bold text-text-main mb-2 font-mono uppercase tracking-wider">
        {t('settings.profile.appearance')}
      </h2>
      <p className="text-text-muted text-sm font-mono mb-6">
        {t('settings.profile.appearanceDescription')}
      </p>

      <div className="space-y-6">
        {/* Theme Selection */}
        <div>
          <label className="block text-sm font-mono font-bold text-text-main uppercase tracking-wider mb-3">
            {t('settings.profile.theme')}
          </label>
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => setTheme('midnight')}
              className={`
                flex items-center gap-2 px-4 py-2 font-mono font-bold uppercase tracking-wider text-sm
                border-2 border-border transition-all duration-150
                ${theme === 'midnight'
                  ? 'bg-accent text-accent-fg shadow-hard'
                  : 'bg-transparent text-text-main hover:shadow-hard'
                }
              `}
            >
              <Moon className="w-4 h-4" />
              {t('settings.profile.themeMidnight')}
            </button>
            <button
              type="button"
              onClick={() => setTheme('paper')}
              className={`
                flex items-center gap-2 px-4 py-2 font-mono font-bold uppercase tracking-wider text-sm
                border-2 border-border transition-all duration-150
                ${theme === 'paper'
                  ? 'bg-accent text-accent-fg shadow-hard'
                  : 'bg-transparent text-text-main hover:shadow-hard'
                }
              `}
            >
              <Sun className="w-4 h-4" />
              {t('settings.profile.themePaper')}
            </button>
          </div>
        </div>

        {/* Language Selection */}
        <div>
          <label className="block text-sm font-mono font-bold text-text-main uppercase tracking-wider mb-3">
            {t('settings.profile.language')}
          </label>
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => setLanguage('cs')}
              className={`
                flex items-center gap-2 px-4 py-2 font-mono font-bold uppercase tracking-wider text-sm
                border-2 border-border transition-all duration-150
                ${language === 'cs'
                  ? 'bg-accent text-accent-fg shadow-hard'
                  : 'bg-transparent text-text-main hover:shadow-hard'
                }
              `}
            >
              Cestina
            </button>
            <button
              type="button"
              onClick={() => setLanguage('en')}
              className={`
                flex items-center gap-2 px-4 py-2 font-mono font-bold uppercase tracking-wider text-sm
                border-2 border-border transition-all duration-150
                ${language === 'en'
                  ? 'bg-accent text-accent-fg shadow-hard'
                  : 'bg-transparent text-text-main hover:shadow-hard'
                }
              `}
            >
              English
            </button>
          </div>
        </div>
      </div>
    </Card>
    </>
  );
}
