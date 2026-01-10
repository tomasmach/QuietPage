import { type HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface SpinnerProps extends Omit<HTMLAttributes<HTMLDivElement>, 'children'> {
  size?: 'sm' | 'md' | 'lg';
}

export function Spinner({ size = 'md', className, ...props }: SpinnerProps) {
  const sizeStyles = {
    sm: 'w-2 h-4',
    md: 'w-3 h-6',
    lg: 'w-4 h-8',
  };

  return (
    <div
      className={cn(
        'inline-block bg-text-main animate-pulse theme-aware',
        sizeStyles[size],
        className
      )}
      role="status"
      aria-label="Loading"
      {...props}
    />
  );
}
