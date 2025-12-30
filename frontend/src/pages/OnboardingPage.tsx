import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme, type Theme } from '@/contexts/ThemeContext';
import { useLanguage, type Language } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface OnboardingData {
  theme: Theme;
  language: Language;
  daily_word_goal: number;
  preferred_writing_time: 'morning' | 'afternoon' | 'evening';
  timezone: string;
}

interface OnboardingPageProps {
  onSkip?: () => void;
}

export function OnboardingPage({ onSkip }: OnboardingPageProps) {
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();
  const { language, setLanguage, t } = useLanguage();

  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [customGoal, setCustomGoal] = useState('');

  const [formData, setFormData] = useState<OnboardingData>({
    theme: theme,
    language: language,
    daily_word_goal: 750,
    preferred_writing_time: 'morning',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  });

  const TOTAL_STEPS = 2;
  const PRESET_GOALS = [250, 500, 750, 1000];

  const handleThemeSelect = (selectedTheme: Theme) => {
    setFormData({ ...formData, theme: selectedTheme });
    setTheme(selectedTheme);
  };

  const handleLanguageSelect = (selectedLanguage: Language) => {
    setFormData({ ...formData, language: selectedLanguage });
    setLanguage(selectedLanguage);
  };

  const handleGoalSelect = (goal: number | 'custom') => {
    if (goal === 'custom') {
      setFormData({ ...formData, daily_word_goal: 0 });
    } else {
      setFormData({ ...formData, daily_word_goal: goal });
      setCustomGoal('');
    }
  };

  const handleCustomGoalChange = (value: string) => {
    setCustomGoal(value);
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue) && numValue > 0) {
      setFormData({ ...formData, daily_word_goal: numValue });
    }
  };

  const handleWritingTimeSelect = (time: 'morning' | 'afternoon' | 'evening') => {
    setFormData({ ...formData, preferred_writing_time: time });
  };

  const handleNext = () => {
    if (step < TOTAL_STEPS) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSkip = () => {
    if (onSkip) {
      onSkip();
    } else {
      navigate('/dashboard');
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Save profile settings (theme, language)
      await api.patch('/settings/profile/', {
        preferred_theme: formData.theme,
        preferred_language: formData.language,
      });

      // Save goals settings (daily word goal, writing time, timezone) and mark onboarding as completed
      await api.patch('/settings/goals/', {
        daily_word_goal: formData.daily_word_goal,
        preferred_writing_time: formData.preferred_writing_time,
        timezone: formData.timezone,
        onboarding_completed: true,
      });

      navigate('/dashboard');
    } catch (error) {
      console.error('Error saving onboarding data:', error);
      // Continue to dashboard even on error
      navigate('/dashboard');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isStep1Valid = true; // Theme and language always have defaults
  const isStep2Valid = formData.daily_word_goal > 0;

  return (
    <div className="min-h-screen bg-bg-main flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-sm font-bold font-mono uppercase tracking-wider text-text-muted">
              {t('onboarding.progress', { current: step, total: TOTAL_STEPS })}
            </h2>
            <button
              onClick={handleSkip}
              className="text-sm font-mono uppercase tracking-wider text-text-muted hover:text-accent transition-colors"
            >
              {t('onboarding.skip')}
            </button>
          </div>
          <div className="w-full h-2 bg-bg-panel border-2 border-border">
            <div
              className="h-full bg-accent transition-all duration-300"
              style={{ width: `${(step / TOTAL_STEPS) * 100}%` }}
            />
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Step 1 - Personalization */}
          {step === 1 && (
            <Card className="space-y-8">
              <div>
                <h1 className="text-2xl font-bold font-mono uppercase tracking-wider text-text-main mb-2">
                  {t('onboarding.step1.title')}
                </h1>
                <p className="text-sm text-text-muted font-mono">
                  {t('onboarding.step1.description')}
                </p>
              </div>

              {/* Theme Selection */}
              <div>
                <label className="block mb-3 text-xs font-bold uppercase tracking-wider text-text-muted font-mono">
                  {t('onboarding.step1.theme')}
                </label>
                <div className="grid grid-cols-2 gap-4">
                  {/* Midnight Theme Card */}
                  <Card
                    hoverable
                    onClick={() => handleThemeSelect('midnight')}
                    className={`cursor-pointer p-4 ${
                      formData.theme === 'midnight'
                        ? 'ring-4 ring-accent shadow-hard'
                        : ''
                    }`}
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-bold font-mono uppercase tracking-wider">
                          {t('themes.midnight')}
                        </h3>
                        {formData.theme === 'midnight' && (
                          <div className="w-3 h-3 bg-accent border-2 border-border" />
                        )}
                      </div>
                      <div className="space-y-2">
                        <div className="h-4 bg-[#0a0a0a] border border-gray-700" />
                        <div className="h-4 bg-[#1a1a1a] border border-gray-700" />
                        <div className="h-4 bg-[#00ff9d] border border-gray-700" />
                      </div>
                    </div>
                  </Card>

                  {/* Paper Theme Card */}
                  <Card
                    hoverable
                    onClick={() => handleThemeSelect('paper')}
                    className={`cursor-pointer p-4 ${
                      formData.theme === 'paper'
                        ? 'ring-4 ring-accent shadow-hard'
                        : ''
                    }`}
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-bold font-mono uppercase tracking-wider">
                          {t('themes.paper')}
                        </h3>
                        {formData.theme === 'paper' && (
                          <div className="w-3 h-3 bg-accent border-2 border-border" />
                        )}
                      </div>
                      <div className="space-y-2">
                        <div className="h-4 bg-[#f5f5dc] border border-gray-400" />
                        <div className="h-4 bg-[#e8e8d0] border border-gray-400" />
                        <div className="h-4 bg-[#2d5016] border border-gray-400" />
                      </div>
                    </div>
                  </Card>
                </div>
              </div>

              {/* Language Selection */}
              <div>
                <label className="block mb-3 text-xs font-bold uppercase tracking-wider text-text-muted font-mono">
                  {t('onboarding.step1.language')}
                </label>
                <div className="flex gap-4">
                  <Button
                    type="button"
                    variant={formData.language === 'cs' ? 'primary' : 'secondary'}
                    onClick={() => handleLanguageSelect('cs')}
                    className="flex-1"
                  >
                    Čeština
                  </Button>
                  <Button
                    type="button"
                    variant={formData.language === 'en' ? 'primary' : 'secondary'}
                    onClick={() => handleLanguageSelect('en')}
                    className="flex-1"
                  >
                    English
                  </Button>
                </div>
              </div>

              {/* Next Button */}
              <div className="flex justify-end">
                <Button
                  type="button"
                  variant="primary"
                  onClick={handleNext}
                  disabled={!isStep1Valid}
                >
                  {t('onboarding.continue')}
                </Button>
              </div>
            </Card>
          )}

          {/* Step 2 - Writing Goals */}
          {step === 2 && (
            <Card className="space-y-8">
              <div>
                <h1 className="text-2xl font-bold font-mono uppercase tracking-wider text-text-main mb-2">
                  {t('onboarding.step2.title')}
                </h1>
                <p className="text-sm text-text-muted font-mono">
                  {t('onboarding.step2.description')}
                </p>
              </div>

              {/* Daily Word Goal */}
              <div>
                <label className="block mb-3 text-xs font-bold uppercase tracking-wider text-text-muted font-mono">
                  {t('onboarding.step2.dailyGoal')}
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                  {PRESET_GOALS.map((goal) => (
                    <Button
                      key={goal}
                      type="button"
                      variant={
                        formData.daily_word_goal === goal &&
                        !customGoal
                          ? 'primary'
                          : 'secondary'
                      }
                      onClick={() => handleGoalSelect(goal)}
                    >
                      {goal}
                    </Button>
                  ))}
                </div>
                <div className="flex items-center gap-4">
                  <Input
                    type="number"
                    value={customGoal}
                    onChange={(e) => handleCustomGoalChange(e.target.value)}
                    placeholder={t('onboarding.step2.customGoalPlaceholder')}
                    min="1"
                    className="flex-1"
                  />
                  <span className="text-xs font-mono uppercase tracking-wider text-text-muted whitespace-nowrap">
                    {t('meta.wordsSuffix')}
                  </span>
                </div>
              </div>

              {/* Preferred Writing Time */}
              <div>
                <label className="block mb-3 text-xs font-bold uppercase tracking-wider text-text-muted font-mono">
                  {t('onboarding.step2.writingTime')}
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <Button
                    type="button"
                    variant={
                      formData.preferred_writing_time === 'morning'
                        ? 'primary'
                        : 'secondary'
                    }
                    onClick={() => handleWritingTimeSelect('morning')}
                  >
                    {t('settings.goals.writingTime.morning')}
                  </Button>
                  <Button
                    type="button"
                    variant={
                      formData.preferred_writing_time === 'afternoon'
                        ? 'primary'
                        : 'secondary'
                    }
                    onClick={() => handleWritingTimeSelect('afternoon')}
                  >
                    {t('settings.goals.writingTime.afternoon')}
                  </Button>
                  <Button
                    type="button"
                    variant={
                      formData.preferred_writing_time === 'evening'
                        ? 'primary'
                        : 'secondary'
                    }
                    onClick={() => handleWritingTimeSelect('evening')}
                  >
                    {t('settings.goals.writingTime.evening')}
                  </Button>
                </div>
              </div>

              {/* Navigation Buttons */}
              <div className="flex justify-between items-center pt-4 border-t-2 border-border border-dashed">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={handleBack}
                >
                  {t('onboarding.back')}
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={!isStep2Valid || isSubmitting}
                  loading={isSubmitting}
                >
                  {isSubmitting ? t('onboarding.finishing') : t('onboarding.finish')}
                </Button>
              </div>
            </Card>
          )}
        </form>
      </div>
    </div>
  );
}
