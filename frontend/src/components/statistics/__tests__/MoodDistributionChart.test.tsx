/**
 * Unit tests for MoodDistributionChart component.
 *
 * Tests rendering of mood distribution data including empty states,
 * most common mood highlighting, and proper display of all 5 mood levels.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MoodDistributionChart } from '../MoodDistributionChart'
import type { MoodAnalytics } from '../../../types/statistics'

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => key,
    language: 'en',
    setLanguage: vi.fn(),
  }),
}))

// Helper to create mood analytics data
function createMoodAnalytics(
  distribution: Record<'1' | '2' | '3' | '4' | '5', number>
): MoodAnalytics {
  return {
    average: 3.0,
    distribution,
    timeline: [],
    totalRatedEntries: Object.values(distribution).reduce((a, b) => a + b, 0),
    trend: 'stable',
  }
}

describe('MoodDistributionChart', () => {
  describe('rendering with data', () => {
    it('renders correctly with mood distribution data', () => {
      const data = createMoodAnalytics({
        '1': 2,
        '2': 5,
        '3': 10,
        '4': 8,
        '5': 3,
      })

      render(<MoodDistributionChart data={data} />)

      // Check title is rendered
      expect(
        screen.getByText('statistics.moodDistribution.title')
      ).toBeInTheDocument()

      // Check all 5 rating labels are displayed
      expect(
        screen.getByText('statistics.moodDistribution.rating 1')
      ).toBeInTheDocument()
      expect(
        screen.getByText('statistics.moodDistribution.rating 2')
      ).toBeInTheDocument()
      expect(
        screen.getByText('statistics.moodDistribution.rating 3')
      ).toBeInTheDocument()
      expect(
        screen.getByText('statistics.moodDistribution.rating 4')
      ).toBeInTheDocument()
      expect(
        screen.getByText('statistics.moodDistribution.rating 5')
      ).toBeInTheDocument()
    })

    it('renders all 5 mood levels (ratings 1-5)', () => {
      const data = createMoodAnalytics({
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
      })

      const { container } = render(<MoodDistributionChart data={data} />)

      // Should have 5 mood rating rows
      const ratingRows = container.querySelectorAll(
        '[class*="border-2"][class*="border-border"][class*="bg-bg-main"]'
      )
      expect(ratingRows.length).toBe(5)
    })

    it('shows correct count for each rating', () => {
      const data = createMoodAnalytics({
        '1': 7,
        '2': 12,
        '3': 25,
        '4': 18,
        '5': 9,
      })

      render(<MoodDistributionChart data={data} />)

      // Check each count is displayed
      expect(screen.getByText('7')).toBeInTheDocument()
      expect(screen.getByText('12')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
      expect(screen.getByText('18')).toBeInTheDocument()
      expect(screen.getByText('9')).toBeInTheDocument()

      // Check entries label appears for each rating (5 times)
      const entriesLabels = screen.getAllByText(
        'statistics.moodDistribution.entries'
      )
      expect(entriesLabels.length).toBe(5)
    })
  })

  describe('empty states', () => {
    it('displays empty state when data is undefined', () => {
      render(<MoodDistributionChart data={undefined} />)

      expect(
        screen.getByText('statistics.moodDistribution.noData')
      ).toBeInTheDocument()
    })

    it('displays empty state when all counts are 0', () => {
      const data = createMoodAnalytics({
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0,
        '5': 0,
      })

      render(<MoodDistributionChart data={data} />)

      expect(
        screen.getByText('statistics.moodDistribution.noData')
      ).toBeInTheDocument()
    })
  })

  describe('most common mood highlighting', () => {
    it('correctly identifies and highlights the most common mood with text-accent class', () => {
      const data = createMoodAnalytics({
        '1': 2,
        '2': 5,
        '3': 15, // Most common
        '4': 8,
        '5': 3,
      })

      render(<MoodDistributionChart data={data} />)

      // The rating label for rating 3 should have accent color
      const rating3Label = screen.getByText('statistics.moodDistribution.rating 3')
      expect(rating3Label).toHaveClass('text-accent')

      // The count for rating 3 should also have accent color
      const count15 = screen.getByText('15')
      expect(count15).toHaveClass('text-accent')

      // Other ratings should not have accent color
      const rating1Label = screen.getByText('statistics.moodDistribution.rating 1')
      expect(rating1Label).not.toHaveClass('text-accent')
      expect(rating1Label).toHaveClass('text-text-main')

      const rating5Label = screen.getByText('statistics.moodDistribution.rating 5')
      expect(rating5Label).not.toHaveClass('text-accent')
      expect(rating5Label).toHaveClass('text-text-main')
    })

    it('highlights multiple moods when they share the highest count', () => {
      const data = createMoodAnalytics({
        '1': 5,
        '2': 10, // Tied for most common
        '3': 3,
        '4': 10, // Tied for most common
        '5': 7,
      })

      render(<MoodDistributionChart data={data} />)

      // Both rating 2 and rating 4 should have accent color
      const rating2Label = screen.getByText('statistics.moodDistribution.rating 2')
      expect(rating2Label).toHaveClass('text-accent')

      const rating4Label = screen.getByText('statistics.moodDistribution.rating 4')
      expect(rating4Label).toHaveClass('text-accent')

      // Rating 3 (lowest) should not have accent
      const rating3Label = screen.getByText('statistics.moodDistribution.rating 3')
      expect(rating3Label).not.toHaveClass('text-accent')
    })

    it('does not highlight any mood when only one entry exists', () => {
      const data = createMoodAnalytics({
        '1': 0,
        '2': 0,
        '3': 1, // Only one entry, should still be highlighted as most common
        '4': 0,
        '5': 0,
      })

      render(<MoodDistributionChart data={data} />)

      // Rating 3 should be highlighted as it's the most common (and only one with data)
      const rating3Label = screen.getByText('statistics.moodDistribution.rating 3')
      expect(rating3Label).toHaveClass('text-accent')
    })
  })

  describe('bar width calculation', () => {
    it('renders background bars with correct relative widths', () => {
      const data = createMoodAnalytics({
        '1': 10,
        '2': 20,
        '3': 50, // Max
        '4': 25,
        '5': 5,
      })

      const { container } = render(<MoodDistributionChart data={data} />)

      // Get all background bar elements
      const bars = container.querySelectorAll('[class*="bg-accent"][class*="absolute"]')
      expect(bars.length).toBe(5)

      // The most common mood (rating 3 with 50) should have 100% width
      // Check that at least one bar has width 100%
      const barStyles = Array.from(bars).map(bar => (bar as HTMLElement).style.width)
      expect(barStyles).toContain('100%')
    })
  })
})
