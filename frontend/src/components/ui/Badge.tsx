import { type HTMLAttributes, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error';
}

export function Badge({ children, variant = 'default', className, ...props }: BadgeProps) {
  const variantStyles = {
    default: 'border-border text-text-main bg-bg-panel theme-aware',
    success: 'border-green-600 text-green-600 bg-green-950/20',
    warning: 'border-yellow-600 text-yellow-600 bg-yellow-950/20',
    error: 'border-red-600 text-red-600 bg-red-950/20',
  };

  return (
    <span
      className={cn(
        'inline-block px-2 py-1 border-2 text-xs uppercase font-bold tracking-wider font-mono',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
