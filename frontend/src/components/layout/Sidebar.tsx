import { Link, useLocation, useNavigate } from 'react-router-dom';
import { PenLine, BarChart3, Archive, Settings, Globe, LogOut } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';
import { useAuth } from '../../contexts/AuthContext';

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { t, language, setLanguage } = useLanguage();
  const { logout } = useAuth();

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
      <div className="mb-8">
        <Link to="/dashboard" className="block">
          <div className="border-2 border-border p-3 inline-flex items-center gap-2 bg-bg-app shadow-hard">
            <div className="w-3 h-3 bg-accent"></div>
            <span className="font-bold text-lg uppercase tracking-widest leading-none text-text-main">QuietPage</span>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                w-full text-left py-2 px-3 border-2 font-bold text-sm uppercase flex justify-between items-center group transition-colors
                ${active
                  ? 'bg-accent text-accent-fg'
                  : 'border-transparent hover:border-border text-text-main'
                }
              `}
            >
              <span className="flex items-center gap-3">
                <Icon size={16} />
                <span>{item.label}</span>
              </span>
              <span className="opacity-0 group-hover:opacity-100 transition-opacity">→</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="mt-auto pt-6 flex flex-col gap-4">
        {/* Logout Button */}
        <button
          onClick={async () => {
            navigate('/');
            await logout();
          }}
          className="w-full text-left py-2 px-3 border-2 border-transparent hover:border-border font-bold text-sm uppercase flex justify-between items-center group transition-colors text-text-main"
          aria-label={t('auth.logout')}
        >
          <span className="flex items-center gap-3">
            <LogOut size={16} />
            <span>{t('auth.logout')}</span>
          </span>
          <span className="opacity-0 group-hover:opacity-100 transition-opacity">→</span>
        </button>

        {/* Language Switcher */}
        <button
          onClick={toggleLanguage}
          className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-text-muted hover:text-text-main transition-colors text-left"
          aria-label="Toggle language"
        >
          <Globe size={14} />
          <span>{language === 'cs' ? 'Jazyk: Cestina' : 'Language: English'}</span>
        </button>

        {/* Version */}
        <div className="text-[10px] uppercase font-bold text-text-muted">
          {t('meta.version')}
        </div>
      </div>
    </div>
  );
}
