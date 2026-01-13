/**
 * Unit tests for WeeklyStats component.
 *
 * Tests rendering of weekly statistics including current streak display,
 * words written this week, best day display, and handling of null/missing data.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { WeeklyStats } from '../WeeklyStats';
import type { WeeklyStats as WeeklyStatsType } from '../../../hooks/useDashboard';

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string, params?: Record<string, unknown>) => {
      if (key === 'dashboard.weeklyStats.streakDays' && params?.count !== undefined) {
        return `${params.count} days`;
      }
      if (key === 'dashboard.weeklyStats.words' && params?.count !== undefined) {
        return `${params.count} words`;
      }
      if (key.startsWith('weekdays.')) {
        const weekday = key.replace('weekdays.', '');
        const weekdayMap: Record<string, string> = {
          monday: 'Monday',
          tuesday: 'Tuesday',
          wednesday: 'Wednesday',
          thursday: 'Thursday',
          friday: 'Friday',
          saturday: 'Saturday',
          sunday: 'Sunday',
        };
        return weekdayMap[weekday] || weekday;
      }
      return key;
    },
    language: 'en',
    setLanguage: vi.fn(),
  }),
}));

describe('WeeklyStats', () => {
  const mockWeeklyStats: WeeklyStatsType = {
    totalWords: 3500,
    bestDay: {
      date: '2025-12-15',
      words: 1200,
      weekday: 'Monday',
    },
  };

  const mockWeeklyStatsNoBestDay: WeeklyStatsType = {
    totalWords: 1500,
    bestDay: null,
  };

  describe('displays current streak', () => {
    it('displays current streak value', () => {
      render(<WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />);

      expect(screen.getByText('15 days')).toBeInTheDocument();
    });

    it('displays streak label', () => {
      render(<WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />);

      expect(
        screen.getByText('dashboard.weeklyStats.streak')
      ).toBeInTheDocument();
    });

    it('displays zero streak correctly', () => {
      render(<WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={0} />);

      expect(screen.getByText('0 days')).toBeInTheDocument();
    });

    it('renders Flame icon for streak', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />
      );

      const svgIcons = container.querySelectorAll('svg');
      expect(svgIcons.length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('displays words this week', () => {
    it('displays total words for the week', () => {
      render(<WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />);

      expect(screen.getByText('3,500 words')).toBeInTheDocument();
    });

    it('displays this week label', () => {
      render(<WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />);

      expect(
        screen.getByText('dashboard.weeklyStats.thisWeek')
      ).toBeInTheDocument();
    });

    it('renders Calendar icon for weekly words', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />
      );

      // Should have multiple icons: Flame, Calendar, and possibly Trophy
      const svgIcons = container.querySelectorAll('svg');
      expect(svgIcons.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('displays best day when available', () => {
    it('displays best day words', () => {
      render(<WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />);

      expect(screen.getByText('1,200 words')).toBeInTheDocument();
    });

    it('displays best day label', () => {
      render(<WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />);

      expect(
        screen.getByText('dashboard.weeklyStats.bestDay')
      ).toBeInTheDocument();
    });

    it('displays weekday name for best day', () => {
      render(<WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />);

      expect(screen.getByText('Monday')).toBeInTheDocument();
    });

    it('renders Trophy icon for best day', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />
      );

      // With best day, should have 3 icons: Flame, Calendar, Trophy
      const svgIcons = container.querySelectorAll('svg');
      expect(svgIcons.length).toBe(3);
    });

    it('translates weekday to localized name', () => {
      const statsWithWednesday: WeeklyStatsType = {
        totalWords: 2000,
        bestDay: {
          date: '2025-12-17',
          words: 800,
          weekday: 'Wednesday',
        },
      };

      render(<WeeklyStats weeklyStats={statsWithWednesday} currentStreak={5} />);

      expect(screen.getByText('Wednesday')).toBeInTheDocument();
    });
  });

  describe('handles null weeklyStats gracefully', () => {
    it('displays 0 words when weeklyStats is null', () => {
      render(<WeeklyStats weeklyStats={null} currentStreak={10} />);

      expect(screen.getByText('0 words')).toBeInTheDocument();
    });

    it('still displays current streak when weeklyStats is null', () => {
      render(<WeeklyStats weeklyStats={null} currentStreak={10} />);

      expect(screen.getByText('10 days')).toBeInTheDocument();
    });

    it('does not display best day section when weeklyStats is null', () => {
      render(<WeeklyStats weeklyStats={null} currentStreak={10} />);

      expect(
        screen.queryByText('dashboard.weeklyStats.bestDay')
      ).not.toBeInTheDocument();
    });

    it('renders only 2 icons when weeklyStats is null', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={null} currentStreak={10} />
      );

      // Without best day, should have 2 icons: Flame, Calendar
      const svgIcons = container.querySelectorAll('svg');
      expect(svgIcons.length).toBe(2);
    });
  });

  describe('hides best day when bestDay is null', () => {
    it('does not render best day section when bestDay is null', () => {
      render(
        <WeeklyStats weeklyStats={mockWeeklyStatsNoBestDay} currentStreak={5} />
      );

      expect(
        screen.queryByText('dashboard.weeklyStats.bestDay')
      ).not.toBeInTheDocument();
    });

    it('still displays words this week when bestDay is null', () => {
      render(
        <WeeklyStats weeklyStats={mockWeeklyStatsNoBestDay} currentStreak={5} />
      );

      expect(screen.getByText('1,500 words')).toBeInTheDocument();
    });

    it('still displays streak when bestDay is null', () => {
      render(
        <WeeklyStats weeklyStats={mockWeeklyStatsNoBestDay} currentStreak={5} />
      );

      expect(screen.getByText('5 days')).toBeInTheDocument();
    });

    it('renders only 2 icons when bestDay is null', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={mockWeeklyStatsNoBestDay} currentStreak={5} />
      );

      // Without best day, should have 2 icons: Flame, Calendar
      const svgIcons = container.querySelectorAll('svg');
      expect(svgIcons.length).toBe(2);
    });
  });

  describe('component structure and styling', () => {
    it('renders stat cards with correct border styling', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />
      );

      const statCards = container.querySelectorAll('.border-2.border-border');
      expect(statCards.length).toBeGreaterThanOrEqual(2);
    });

    it('stat cards have panel background', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />
      );

      const panelCards = container.querySelectorAll('.bg-bg-panel');
      expect(panelCards.length).toBeGreaterThanOrEqual(2);
    });

    it('stat cards have shadow styling', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />
      );

      const shadowCards = container.querySelectorAll('.shadow-hard');
      expect(shadowCards.length).toBeGreaterThanOrEqual(2);
    });

    it('displays large text for stat values', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />
      );

      const largeText = container.querySelectorAll('.text-2xl');
      expect(largeText.length).toBeGreaterThanOrEqual(2);
    });

    it('labels have uppercase styling', () => {
      const { container } = render(
        <WeeklyStats weeklyStats={mockWeeklyStats} currentStreak={15} />
      );

      const uppercaseLabels = container.querySelectorAll('.uppercase');
      expect(uppercaseLabels.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('number formatting', () => {
    it('formats large word counts with locale separators', () => {
      const largeStats: WeeklyStatsType = {
        totalWords: 12500,
        bestDay: {
          date: '2025-12-15',
          words: 5000,
          weekday: 'Friday',
        },
      };

      render(<WeeklyStats weeklyStats={largeStats} currentStreak={100} />);

      expect(screen.getByText('12,500 words')).toBeInTheDocument();
      expect(screen.getByText('5,000 words')).toBeInTheDocument();
    });

    it('handles small word counts', () => {
      const smallStats: WeeklyStatsType = {
        totalWords: 50,
        bestDay: {
          date: '2025-12-15',
          words: 25,
          weekday: 'Tuesday',
        },
      };

      render(<WeeklyStats weeklyStats={smallStats} currentStreak={1} />);

      expect(screen.getByText('50 words')).toBeInTheDocument();
      expect(screen.getByText('25 words')).toBeInTheDocument();
    });
  });
});
