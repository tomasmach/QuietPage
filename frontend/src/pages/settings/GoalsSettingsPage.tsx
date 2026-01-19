import { useState, type FormEvent } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useSettings } from '@/hooks/useSettings';
import { useToast } from '@/contexts/ToastContext';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { SEO } from '@/components/SEO';

// Common timezones
const TIMEZONES = [
  'Europe/Prague',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'America/New_York',
  'America/Los_Angeles',
  'America/Chicago',
  'Asia/Tokyo',
  'Asia/Shanghai',
  'Australia/Sydney',
  'UTC',
];

type WritingTime = 'morning' | 'afternoon' | 'evening';

const WRITING_TIMES: WritingTime[] = ['morning', 'afternoon', 'evening'];

export function GoalsSettingsPage() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const { isLoading, clearMessages, updateGoals } = useSettings();
  const toast = useToast();

  const [formData, setFormData] = useState({
    daily_word_goal: user?.daily_word_goal || 750,
    timezone: user?.timezone || 'Europe/Prague',
    preferred_writing_time: (user?.preferred_writing_time || 'morning') as WritingTime,
    reminder_enabled: user?.reminder_enabled || false,
    reminder_time: user?.reminder_time || '09:00',
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearMessages();
    const result = await updateGoals(formData);
    if (result) {
      toast.success(t('toast.goalsUpdated'));
    } else {
      toast.error(t('toast.saveError'));
    }
  };

  return (
    <>
      <SEO title="Goals Settings" description="Set your daily writing goals and preferred writing times." />
      <Card>
        <h2 className="text-2xl font-bold text-text-main mb-6 font-mono uppercase tracking-wider">
          {t('settings.goals.title')}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Daily Word Goal */}
        <div className="w-full">
          <label
            htmlFor="daily_word_goal"
            className="block mb-2 text-xs font-bold uppercase tracking-wider text-text-muted font-mono"
          >
            {t('settings.goals.dailyWordGoal')}
          </label>
          <Input
            id="daily_word_goal"
            type="number"
            min={100}
            max={5000}
            step={50}
            value={formData.daily_word_goal}
            onChange={(e) =>
              setFormData({ ...formData, daily_word_goal: parseInt(e.target.value) || 750 })
            }
            disabled={isLoading}
            helperText={t('settings.goals.dailyWordGoalHint')}
          />
        </div>

        {/* Timezone */}
        <div className="w-full">
          <label
            htmlFor="timezone"
            className="block mb-2 text-xs font-bold uppercase tracking-wider text-text-muted font-mono"
          >
            {t('settings.goals.timezone')}
          </label>
          <select
            id="timezone"
            value={formData.timezone}
            onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
            disabled={isLoading}
            className="w-full bg-bg-panel border-2 border-border text-text-main font-mono px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent"
          >
            {TIMEZONES.map((tz) => (
              <option key={tz} value={tz}>
                {tz}
              </option>
            ))}
          </select>
        </div>

        {/* Preferred Writing Time */}
        <div className="w-full">
          <label
            htmlFor="preferred_writing_time"
            className="block mb-2 text-xs font-bold uppercase tracking-wider text-text-muted font-mono"
          >
            {t('settings.goals.preferredWritingTime')}
          </label>
          <select
            id="preferred_writing_time"
            value={formData.preferred_writing_time}
            onChange={(e) =>
              setFormData({ ...formData, preferred_writing_time: e.target.value as WritingTime })
            }
            disabled={isLoading}
            className="w-full bg-bg-panel border-2 border-border text-text-main font-mono px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent"
          >
            {WRITING_TIMES.map((time) => (
              <option key={time} value={time}>
                {t(`settings.goals.writingTime.${time}`)}
              </option>
            ))}
          </select>
        </div>

        {/* Reminder Section */}
        <div className="border-t-2 border-border pt-6 mt-6">
          <h3 className="text-lg font-bold text-text-main mb-4 font-mono uppercase tracking-wider">
            {t('settings.goals.reminders')}
          </h3>

          {/* Reminder Enabled */}
          <div className="flex items-center gap-3 mb-4">
            <input
              type="checkbox"
              id="reminder_enabled"
              checked={formData.reminder_enabled}
              onChange={(e) => setFormData({ ...formData, reminder_enabled: e.target.checked })}
              disabled={isLoading}
              className="w-5 h-5 border-2 border-border bg-bg-panel accent-accent cursor-pointer"
            />
            <label
              htmlFor="reminder_enabled"
              className="text-sm font-mono text-text-main cursor-pointer"
            >
              {t('settings.goals.enableReminders')}
            </label>
          </div>

          {/* Reminder Time */}
          {formData.reminder_enabled && (
            <div className="w-full">
              <label
                htmlFor="reminder_time"
                className="block mb-2 text-xs font-bold uppercase tracking-wider text-text-muted font-mono"
              >
                {t('settings.goals.reminderTime')}
              </label>
              <input
                type="time"
                id="reminder_time"
                value={formData.reminder_time}
                onChange={(e) => setFormData({ ...formData, reminder_time: e.target.value })}
                disabled={isLoading}
                className="w-full bg-bg-panel border-2 border-border text-text-main font-mono px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent"
              />
            </div>
          )}
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
