import { BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Logo({ size = 'md', className }: LogoProps) {
  const sizeStyles = {
    sm: 'gap-2 p-2',
    md: 'gap-3 p-3',
    lg: 'gap-4 p-4',
  };

  const iconSizes = {
    sm: 20,
    md: 28,
    lg: 36,
  };

  const textSizes = {
    sm: 'text-xl',
    md: 'text-3xl',
    lg: 'text-5xl',
  };

  return (
    <div
      className={cn(
        'inline-flex items-center bg-bg-panel border-2 border-border shadow-hard font-mono font-bold theme-aware',
        sizeStyles[size],
        className
      )}
    >
      <BookOpen size={iconSizes[size]} className="text-accent theme-aware" />
      <span className={cn('text-text-main theme-aware', textSizes[size])}>QUIETPAGE</span>
    </div>
  );
}
