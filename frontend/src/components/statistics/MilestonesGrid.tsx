import { Trophy, Star, Target, Flame, Check } from 'lucide-react';
import type { Milestones, MilestoneType } from '../../types/statistics';
import { useLanguage } from '../../contexts/LanguageContext';

interface MilestonesGridProps {
  data: Milestones | undefined;
}

interface MilestoneBadgeProps {
  type: MilestoneType;
  value: number;
  achieved: boolean;
  current: number;
}

/**
 * Returns the appropriate icon component for each milestone type.
 */
function getMilestoneIcon(type: MilestoneType, achieved: boolean) {
  const iconClass = achieved ? 'theme-aware text-accent-fg' : 'theme-aware text-text-muted';
  const size = 20;
  const strokeWidth = 2;

  switch (type) {
    case 'entries':
      return <Target size={size} strokeWidth={strokeWidth} className={iconClass} />;
    case 'words':
      return <Star size={size} strokeWidth={strokeWidth} className={iconClass} />;
    case 'streak':
      return <Flame size={size} strokeWidth={strokeWidth} className={iconClass} />;
    default:
      return <Trophy size={size} strokeWidth={strokeWidth} className={iconClass} />;
  }
}

/**
 * Formats large numbers for display (e.g., 10000 -> "10k").
 */
function formatValue(value: number): string {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(value % 1000000 === 0 ? 0 : 1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(value % 1000 === 0 ? 0 : 1)}k`;
  }
  return value.toString();
}

/**
 * MilestoneBadge displays an individual milestone with its achievement status.
 */
function MilestoneBadge({ type, value, achieved, current }: MilestoneBadgeProps) {
  const { t } = useLanguage();

  // Calculate progress percentage toward the milestone
  const progressPercent = achieved ? 100 : Math.min((current / value) * 100, 99);

  // Get the label for this milestone type
  const getTypeLabel = () => {
    switch (type) {
      case 'entries':
        return t('statistics.milestones.entries');
      case 'words':
        return t('statistics.milestones.words');
      case 'streak':
        return t('statistics.milestones.streaks');
      default:
        return type;
    }
  };

  return (
    <div
      className={`
        theme-aware relative border-2 font-mono transition-all duration-150 flex items-center gap-4 p-4
        ${achieved
          ? 'bg-accent text-accent-fg border-border shadow-hard'
          : 'bg-bg-panel text-text-muted border-dashed border-border'
        }
        rounded-none
      `}
    >
      {/* Icon */}
      <div className={`
        theme-aware flex items-center justify-center w-12 h-12 border-2 flex-shrink-0
        ${achieved ? 'border-accent-fg bg-accent' : 'border-border bg-bg-panel'}
        rounded-none
      `}>
        {getMilestoneIcon(type, achieved)}
      </div>

      {/* Value and label */}
      <div className="flex-shrink-0">
        <p className={`theme-aware text-2xl font-bold leading-none mb-1 ${achieved ? 'text-accent-fg' : 'text-text-main'}`}>
          {formatValue(value)}
        </p>
        <p className={`theme-aware text-[10px] uppercase tracking-widest leading-none ${achieved ? 'text-accent-fg opacity-80' : 'text-text-muted'}`}>
          {getTypeLabel()}
        </p>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Status section */}
      {achieved ? (
        /* Achieved indicator */
        <div className="flex items-center gap-3">
          <p className="theme-aware text-[10px] uppercase tracking-widest font-bold text-accent-fg">
            {t('statistics.milestones.achieved')}
          </p>
          <div className="theme-aware flex items-center justify-center w-6 h-6 bg-accent-fg rounded-none">
            <Check size={14} strokeWidth={3} className="theme-aware text-accent" />
          </div>
        </div>
      ) : (
        /* Progress bar for unachieved milestones */
        <div className="flex items-center gap-4 min-w-0 flex-1 max-w-md">
          <div className="flex-1 min-w-0">
            <div className="flex justify-between items-center mb-2">
              <span className="theme-aware text-[10px] uppercase tracking-widest text-text-muted">
                {formatValue(current)} / {formatValue(value)}
              </span>
              <span className="theme-aware text-[10px] font-bold text-text-muted ml-2">
                {Math.round(progressPercent)}%
              </span>
            </div>
            <div className="theme-aware h-2 border-2 border-border bg-bg-app rounded-none overflow-hidden">
              <div
                className="theme-aware h-full bg-text-muted transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * MilestonesGrid displays achievement milestones organized by category.
 * 
 * Milestones are badges that celebrate user progress:
 * - Entries: Number of journal entries written
 * - Words: Total word count achieved
 * - Streaks: Consecutive days of writing
 * 
 * Achieved milestones are highlighted with accent colors and shadows.
 * Unachieved milestones show progress toward the next goal.
 */
export function MilestonesGrid({ data }: MilestonesGridProps) {
  const { t } = useLanguage();

  // Group milestones by type
  const groupedMilestones = {
    entries: data?.milestones.filter(m => m.type === 'entries') || [],
    words: data?.milestones.filter(m => m.type === 'words') || [],
    streak: data?.milestones.filter(m => m.type === 'streak') || [],
  };

  // Check if there's any data
  const hasMilestones = data?.milestones && data.milestones.length > 0;

  if (!hasMilestones) {
    return (
      <div className="theme-aware border-2 border-border bg-bg-panel p-8 text-center rounded-none shadow-hard">
        <Trophy size={32} strokeWidth={2} className="theme-aware text-text-muted mx-auto mb-4" />
        <h3 className="theme-aware text-xs font-bold uppercase tracking-widest text-text-main mb-2 font-mono">
          {t('statistics.milestones.title')}
        </h3>
        <p className="theme-aware text-text-muted font-mono text-sm">
          {t('statistics.milestones.noData')}
        </p>
      </div>
    );
  }

  const renderCategory = (type: MilestoneType, milestones: typeof groupedMilestones.entries) => {
    if (milestones.length === 0) return null;

    const getCategoryLabel = () => {
      switch (type) {
        case 'entries':
          return t('statistics.milestones.entries');
        case 'words':
          return t('statistics.milestones.words');
        case 'streak':
          return t('statistics.milestones.streaks');
        default:
          return type;
      }
    };

    return (
      <div key={type} className="mb-8 last:mb-0">
        <h4 className="theme-aware text-[10px] font-bold uppercase tracking-widest text-text-muted mb-4 font-mono">
          {getCategoryLabel()}
        </h4>
        <div className="space-y-3">
          {milestones.map((milestone, index) => (
            <MilestoneBadge
              key={`${milestone.type}-${milestone.value}-${index}`}
              type={milestone.type}
              value={milestone.value}
              achieved={milestone.achieved}
              current={milestone.current}
            />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="theme-aware border-2 border-border bg-bg-panel p-6 shadow-hard rounded-none">
      <h3 className="theme-aware text-xs font-bold uppercase tracking-widest text-text-main mb-6 font-mono flex items-center gap-2">
        <Trophy size={16} strokeWidth={2} />
        {t('statistics.milestones.title')}
      </h3>

      {renderCategory('entries', groupedMilestones.entries)}
      {renderCategory('words', groupedMilestones.words)}
      {renderCategory('streak', groupedMilestones.streak)}
    </div>
  );
}
