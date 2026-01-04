import { type ImgHTMLAttributes, useState } from 'react';
import { cn } from '@/lib/utils';

export interface AvatarProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src'> {
  src?: string;
  alt: string;
  size?: 'sm' | 'md' | 'lg';
  fallback?: string;
}

export function Avatar({ src, alt, size = 'md', fallback, className, ...props }: AvatarProps) {
  const [imageError, setImageError] = useState(false);

  const sizeStyles = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-12 h-12 text-base',
    lg: 'w-16 h-16 text-xl',
  };

  const showFallback = !src || imageError;
  const fallbackInitial = fallback?.charAt(0).toUpperCase() || alt.charAt(0).toUpperCase();

  return (
    <div
      className={cn(
        'border-2 border-border bg-bg-panel flex items-center justify-center overflow-hidden',
        sizeStyles[size],
        className
      )}
    >
      {showFallback ? (
        <span className="font-mono font-bold text-text-main" aria-label={alt}>
          {fallbackInitial}
        </span>
      ) : (
        <img
          src={src}
          alt={alt}
          onError={() => setImageError(true)}
          className="w-full h-full object-cover"
          {...props}
        />
      )}
    </div>
  );
}
