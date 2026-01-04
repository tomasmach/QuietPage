import { type LucideIcon } from 'lucide-react';

interface AnimatedIconProps {
  icon: LucideIcon;
  size?: number;
  animation?: 'float' | 'pulse' | 'flicker' | 'none';
  className?: string;
}

export const AnimatedIcon: React.FC<AnimatedIconProps> = ({
  icon: Icon,
  size = 48,
  animation = 'none',
  className = '',
}) => {
  const animationClass = {
    float: 'float-animation',
    pulse: 'pulse-animation',
    flicker: 'flicker-animation',
    none: '',
  }[animation];

  const animationStyle = {
    float: { animation: 'float 3s ease-in-out infinite' },
    pulse: { animation: 'pulse-subtle 2s ease-in-out infinite' },
    flicker: { animation: 'flicker 1.5s ease-in-out infinite' },
    none: {},
  }[animation];

  return (
    <div
      className={`inline-block ${animationClass} ${className}`}
      style={animationStyle}
    >
      <Icon size={size} />
    </div>
  );
};
