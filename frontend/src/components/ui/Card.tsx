import { type HTMLAttributes, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hoverable?: boolean;
}

export function Card({ children, className, hoverable = false, onClick, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'bg-bg-panel border-2 border-border shadow-hard p-6',
        hoverable &&
          'cursor-pointer hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all duration-150',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick(e as any);
              }
            }
          : undefined
      }
      {...props}
    >
      {children}
    </div>
  );
}
