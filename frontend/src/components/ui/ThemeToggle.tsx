import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50
        p-4 rounded-none border-2 border-border bg-background text-primary
        shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]
        transition-all duration-200
        hover:-translate-y-0.5"
      aria-label={theme === 'midnight' ? 'Switch to light theme' : 'Switch to dark theme'}
    >
      {theme === 'midnight' ? (
        <Sun size={24} className="text-primary" />
      ) : (
        <Moon size={24} className="text-primary" />
      )}
    </button>
  );
}
