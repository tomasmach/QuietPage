import { Link, useLocation } from 'react-router-dom';
import { PenLine, BarChart3, Archive, Settings, Globe } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';

export function Sidebar() {
  const location = useLocation();
  const { t, language, setLanguage } = useLanguage();

  const navItems = [
    { path: '/dashboard', icon: PenLine, label: t('nav.write') },
    { path: '/stats', icon: BarChart3, label: t('nav.stats') },
    { path: '/archive', icon: Archive, label: t('nav.archive') },
    { path: '/settings', icon: Settings, label: t('nav.settings') },
  ];

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const toggleLanguage = () => {
    setLanguage(language === 'cs' ? 'en' : 'cs');
  };

  return (
    <div className="flex flex-col h-full p-6">
      {/* Logo */}
      <div className="mb-12">
        <Link to="/dashboard" className="block">
          <h1 className="text-2xl font-bold text-primary tracking-tight">
            QuietPage
          </h1>
          <div
            className="absolute mt-1 ml-1 w-full h-1 bg-primary/20 -z-10"
            style={{ transform: 'translateY(-4px)' }}
          />
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-none
                border-2 transition-all
                ${active
                  ? 'bg-primary text-background border-primary shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'
                  : 'bg-background text-text border-border hover:border-primary'
                }
              `}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Language Switcher */}
      <div className="mt-auto pt-6 space-y-4 border-t-2 border-border">
        <button
          onClick={toggleLanguage}
          className="flex items-center gap-3 px-4 py-3 w-full rounded-none
            border-2 border-border bg-background text-text
            hover:border-primary transition-all"
          aria-label="Toggle language"
        >
          <Globe size={20} />
          <span className="font-medium">
            {language === 'cs' ? 'Čeština' : 'English'}
          </span>
        </button>

        {/* Version */}
        <div className="text-xs text-muted text-center">
          {t('meta.version')}
        </div>
      </div>
    </div>
  );
}
