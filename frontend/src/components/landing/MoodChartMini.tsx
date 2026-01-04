import { Frown, Meh, Smile, Laugh } from 'lucide-react';

export const MoodChartMini: React.FC = () => {
  // Mock data: 7 mood values (1-5 scale)
  const moodData = [3, 4, 2, 4, 5, 4, 5];

  // SVG dimensions
  const width = 280;
  const height = 120;
  const padding = 20;

  // Calculate points for the line
  const maxMood = 5;
  const minMood = 1;
  const pointSpacing = (width - padding * 2) / (moodData.length - 1);

  const points = moodData.map((mood, index) => {
    const x = padding + index * pointSpacing;
    const y = height - padding - ((mood - minMood) / (maxMood - minMood)) * (height - padding * 2);
    return { x, y, mood };
  });

  // Create path string
  const pathD = points.map((point, index) => {
    if (index === 0) {
      return `M ${point.x},${point.y}`;
    }
    return `L ${point.x},${point.y}`;
  }).join(' ');

  // Calculate path length for animation
  const pathLength = 1000;

  // Mood icons mapping
  const getMoodIcon = (mood: number) => {
    if (mood <= 2) return Frown;
    if (mood === 3) return Meh;
    if (mood === 4) return Smile;
    return Laugh;
  };

  return (
    <div className="w-full max-w-[280px] mx-auto my-4">
      <svg
        width="100%"
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        className="overflow-visible"
      >
        {/* Grid lines */}
        {[1, 2, 3, 4, 5].map((level) => {
          const y = height - padding - ((level - minMood) / (maxMood - minMood)) * (height - padding * 2);
          return (
            <line
              key={level}
              x1={padding}
              y1={y}
              x2={width - padding}
              y2={y}
              stroke="currentColor"
              strokeOpacity="0.1"
              strokeWidth="1"
            />
          );
        })}

        {/* Animated line path */}
        <path
          d={pathD}
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={pathLength}
          strokeDashoffset={pathLength}
          className="draw-animation"
          style={{
            animation: 'draw-line 2s ease-out forwards',
          }}
        />

        {/* Data points */}
        {points.map((point, index) => (
          <circle
            key={index}
            cx={point.x}
            cy={point.y}
            r="4"
            fill="var(--color-accent)"
            stroke="var(--color-bg-panel)"
            strokeWidth="2"
            opacity="0"
            style={{
              animation: `pulse-subtle 2s ease-out ${index * 0.15}s forwards`,
            }}
          />
        ))}
      </svg>

      {/* Mood icons below chart */}
      <div className="flex justify-between items-center mt-2 px-4">
        {points.slice(0, 7).map((point, index) => {
          const MoodIcon = getMoodIcon(point.mood);
          return (
            <div
              key={index}
              className="opacity-0"
              style={{
                animation: `pulse-subtle 0.5s ease-out ${0.3 + index * 0.1}s forwards`,
              }}
            >
              <MoodIcon size={16} className="text-text-muted" />
            </div>
          );
        })}
      </div>
    </div>
  );
};
