import { Globe } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';

export function LanguageToggle() {
  const { language, setLanguage } = useLanguage();

  const toggleLanguage = () => {
    setLanguage(language === 'cs' ? 'en' : 'cs');
  };

  return (
    <button
      onClick={toggleLanguage}
      className="fixed top-4 left-4 z-50
        p-3 border-2 border-border bg-bg-panel text-text-main
        shadow-hard hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none
        transition-all duration-150 font-mono font-bold text-sm
        inline-flex items-center gap-2"
      aria-label={`Switch to ${language === 'cs' ? 'English' : 'Czech'}`}
    >
      <Globe size={20} className="text-accent" />
      <span className="uppercase">{language === 'cs' ? 'CS' : 'EN'}</span>
    </button>
  );
}
