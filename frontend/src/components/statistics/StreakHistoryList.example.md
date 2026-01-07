# StreakHistoryList Component Usage Example

## Overview
The `StreakHistoryList` component displays the top 5 historical streaks with gamification elements.

## Basic Usage

```tsx
import { StreakHistoryList } from '../components/statistics/StreakHistoryList';
import type { WritingPatterns } from '../types/statistics';

// In your statistics page or component
export function StatsPage() {
  const { data } = useStatistics('30d');
  
  return (
    <div className="space-y-8">
      {/* Other statistics components */}
      
      {/* Streak History */}
      <StreakHistoryList data={data.writingPatterns} />
    </div>
  );
}
```

## Example in StatsPage.tsx

Add this to the existing StatsPage:

```tsx
import { StreakHistoryList } from '../components/statistics/StreakHistoryList';

// ... existing imports

export function StatsPage() {
  // ... existing code
  
  return (
    <AppLayout sidebar={<Sidebar />} contextPanel={<ContextPanel />}>
      <div className="p-8 space-y-8">
        {/* ... existing header and time selector */}
        
        {data ? (
          <div className="space-y-8">
            <StatsSummaryCards data={data} />
            
            {/* Add Streak History */}
            <StreakHistoryList data={data.writingPatterns} />
            
            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <MoodTimelineChart data={data.moodAnalytics} />
              <WordCountTimelineChart data={data.wordCountAnalytics} />
            </div>
          </div>
        ) : null}
      </div>
    </AppLayout>
  );
}
```

## Features

1. **Top 5 Streaks**: Displays up to 5 longest streaks in descending order
2. **Longest Streak Badge**: Highlights the longest streak with inverted colors (accent background)
3. **Current Streak Badge**: Shows if a streak is currently active
4. **Gamification Messages**:
   - If current streak > longest: "Congrats! Your current streak (X days) is a new record!"
   - If current streak = longest: "Amazing! You matched your record of X days!"
   - If current streak < longest: "Your longest streak was X days – you can beat it!"
5. **Localized Dates**: Formats dates based on user's language (cs-CZ or en-US)
6. **Brutalist Design**: Hard shadows, sharp borders, monospace font (IBM Plex Mono)
7. **Theme Support**: Works with both Midnight (dark) and Paper (light) themes

## Design Details

### Color Usage
- **Longest streak**: Uses accent color (white on dark bg in Midnight, black on light bg in Paper)
- **Regular streaks**: Uses panel background with text-main color
- **Badges**: Border with accent color
- **Hover effects**: Subtle translation effect on longest streak, background change on others

### Typography
- **Headers**: Uppercase, bold, tracking-widest, text-xs
- **Dates**: Regular weight, text-sm
- **Streak count**: Large, bold, text-2xl
- **All text**: IBM Plex Mono font

### Layout
- **Border**: 2px solid border-border
- **Shadow**: Hard shadow (4px 4px) on container
- **Padding**: Generous 6 (1.5rem) padding
- **Dividers**: 2px solid between streak items

## Translation Keys

The component uses the following translation keys:

```typescript
// Czech (cs)
statistics.streakHistory.title // "HISTORIE STREAKU"
statistics.streakHistory.noData // "Zatím žádná data o streaku"
statistics.streakHistory.longest // "Nejdelší"
statistics.streakHistory.current // "Aktuální"
statistics.streakHistory.daySingular // "den"
statistics.streakHistory.daysPlural // "dní"
statistics.streakHistory.encouragement // "Tvůj nejdelší streak byl {days} dní – můžeš ho překonat!"
statistics.streakHistory.newRecord // "Gratulujeme! Tvůj aktuální streak ({days} dní) je nový rekord!"
statistics.streakHistory.matchingRecord // "Skvělé! Vyrovnal jsi svůj rekord {days} dní!"

// English (en)
statistics.streakHistory.title // "STREAK HISTORY"
statistics.streakHistory.noData // "No streak history yet"
statistics.streakHistory.longest // "Longest"
statistics.streakHistory.current // "Current"
statistics.streakHistory.daySingular // "day"
statistics.streakHistory.daysPlural // "days"
statistics.streakHistory.encouragement // "Your longest streak was {days} days – you can beat it!"
statistics.streakHistory.newRecord // "Congrats! Your current streak ({days} days) is a new record!"
statistics.streakHistory.matchingRecord // "Amazing! You matched your record of {days} days!"
```

## Data Requirements

The component expects `WritingPatterns` type with `streakHistory` array:

```typescript
interface WritingPatterns {
  streakHistory: {
    startDate: string;  // ISO date string
    endDate: string;    // ISO date string
    length: number;     // Number of days
  }[];
  // ... other properties
}
```
