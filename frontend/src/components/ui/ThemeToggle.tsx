import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="fixed top-4 right-4 z-50
        p-3 border-2 border-border bg-bg-panel text-text-main
        shadow-hard hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none
        transition-all duration-150 theme-aware"
      aria-label={theme === 'midnight' ? 'Switch to light theme' : 'Switch to dark theme'}
    >
      {theme === 'midnight' ? (
        <Sun size={20} className="text-accent theme-aware" />
      ) : (
        <Moon size={20} className="text-accent theme-aware" />
      )}
    </button>
  );
}
