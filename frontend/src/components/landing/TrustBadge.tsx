import { type LucideIcon } from 'lucide-react';

interface TrustBadgeProps {
  icon: LucideIcon;
  text: string;
  variant?: 'default' | 'highlighted';
}

export const TrustBadge: React.FC<TrustBadgeProps> = ({
  icon: Icon,
  text,
  variant = 'default',
}) => {
  const baseClasses = 'inline-flex items-center gap-2 px-3 py-1.5 border-2 text-xs font-bold uppercase tracking-wider';
  const variantClasses = {
    default: 'bg-bg-panel border-border text-text-muted',
    highlighted: 'bg-accent border-border text-accent-fg',
  }[variant];

  return (
    <div className={`${baseClasses} ${variantClasses}`}>
      <Icon size={14} />
      <span>{text}</span>
    </div>
  );
};
