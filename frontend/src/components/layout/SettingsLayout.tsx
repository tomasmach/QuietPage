import { Link, useLocation, Outlet } from 'react-router-dom';
import { User, Target, Shield, Lock, Trash2 } from 'lucide-react';
import { AppLayout } from './AppLayout';
import { Sidebar } from './Sidebar';
import { ContextPanel } from './ContextPanel';
import { useLanguage } from '../../contexts/LanguageContext';

interface SettingsNavItem {
  path: string;
  icon: React.ComponentType<{ size?: number }>;
  labelKey: keyof ReturnType<typeof useTranslations>['nav'];
  danger?: boolean;
}

function useTranslations() {
  const { t } = useLanguage();
  return {
    nav: {
      profile: t('settings.nav.profile'),
      goals: t('settings.nav.goals'),
      privacy: t('settings.nav.privacy'),
      security: t('settings.nav.security'),
      deleteAccount: t('settings.nav.deleteAccount'),
    },
    title: t('settings.title'),
  };
}

export function SettingsLayout() {
  const location = useLocation();
  const translations = useTranslations();

  const navItems: SettingsNavItem[] = [
    { path: '/settings/profile', icon: User, labelKey: 'profile' },
    { path: '/settings/goals', icon: Target, labelKey: 'goals' },
    { path: '/settings/privacy', icon: Shield, labelKey: 'privacy' },
    { path: '/settings/security', icon: Lock, labelKey: 'security' },
    { path: '/settings/delete-account', icon: Trash2, labelKey: 'deleteAccount', danger: true },
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
      <div className="p-8">
        <h1 className="text-4xl font-bold text-primary mb-8">{translations.title}</h1>

        <div className="flex gap-8">
          {/* Settings Navigation */}
          <nav className="w-64 flex-shrink-0 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center gap-3 px-4 py-3
                    border-2 transition-all font-mono text-sm uppercase tracking-wider
                    ${active
                      ? item.danger
                        ? 'bg-red-600 text-white border-red-800 shadow-hard'
                        : 'bg-primary text-bg-panel border-primary shadow-hard'
                      : item.danger
                        ? 'bg-bg-panel text-red-600 border-border hover:border-red-600'
                        : 'bg-bg-panel text-text-main border-border hover:border-primary'
                    }
                  `}
                >
                  <Icon size={18} />
                  <span className="font-bold">{translations.nav[item.labelKey]}</span>
                </Link>
              );
            })}
          </nav>

          {/* Settings Content */}
          <div className="flex-1 min-w-0">
            <Outlet />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
