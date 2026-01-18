import { cn } from '@/lib/utils';

export interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showText?: boolean;
}

/**
 * Custom brutalist geometric logo icon
 * Represents stacked journal pages with hard shadow
 */
function LogoIcon({ size = 28 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="QuietPage"
      className="theme-aware"
    >
      {/* Hard shadow layer - signature brutalist effect */}
      <rect
        x="34"
        y="34"
        width="50"
        height="50"
        fill="var(--color-shadow)"
      />

      {/* Back page (subtle depth) */}
      <rect
        x="20"
        y="40"
        width="50"
        height="50"
        fill="var(--color-text-muted)"
        stroke="var(--color-border)"
        strokeWidth="2"
      />

      {/* Middle page */}
      <rect
        x="25"
        y="30"
        width="50"
        height="50"
        fill="var(--color-bg-panel)"
        stroke="var(--color-border)"
        strokeWidth="2"
      />

      {/* Front page with writing lines */}
      <g>
        <rect
          x="30"
          y="30"
          width="50"
          height="50"
          fill="var(--color-accent)"
          stroke="var(--color-border)"
          strokeWidth="2"
        />
        {/* Three horizontal lines representing text */}
        <line
          x1="38"
          y1="42"
          x2="68"
          y2="42"
          stroke="var(--color-accent-fg)"
          strokeWidth="2"
        />
        <line
          x1="38"
          y1="52"
          x2="68"
          y2="52"
          stroke="var(--color-accent-fg)"
          strokeWidth="2"
        />
        <line
          x1="38"
          y1="62"
          x2="55"
          y2="62"
          stroke="var(--color-accent-fg)"
          strokeWidth="2"
        />
      </g>
    </svg>
  );
}

export function Logo({ size = 'md', className, showText = true }: LogoProps) {
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
      <LogoIcon size={iconSizes[size]} />
      {showText && (
        <span className={cn('text-text-main theme-aware', textSizes[size])}>
          QUIETPAGE
        </span>
      )}
    </div>
  );
}
