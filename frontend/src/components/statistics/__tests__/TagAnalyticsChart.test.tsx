/**
 * Unit tests for TagAnalyticsChart component.
 *
 * Tests rendering of tag analytics data including empty states,
 * top 10 tag limiting, and proper display of tag metrics.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TagAnalyticsChart } from '../TagAnalyticsChart'
import type { TagAnalytics, TagData } from '../../../types/statistics'

// Mock the useLanguage hook
vi.mock('../../../contexts/LanguageContext', () => ({
  useLanguage: () => ({
    t: (key: string) => key,
    language: 'en',
    setLanguage: vi.fn(),
  }),
}))

// Helper to create tag data
function createTag(overrides: Partial<TagData> = {}): TagData {
  return {
    name: 'test-tag',
    entryCount: 5,
    totalWords: 1000,
    averageWords: 200,
    averageMood: 3.5,
    ...overrides,
  }
}

// Helper to create tag analytics data
function createTagAnalytics(
  tags: TagData[],
  totalTags?: number
): TagAnalytics {
  return {
    tags,
    totalTags: totalTags ?? tags.length,
  }
}

describe('TagAnalyticsChart', () => {
  describe('rendering with data', () => {
    it('renders correctly with tag data', () => {
      const data = createTagAnalytics([
        createTag({ name: 'journal', entryCount: 10, averageWords: 500 }),
        createTag({ name: 'work', entryCount: 5, averageWords: 300 }),
      ])

      render(<TagAnalyticsChart data={data} />)

      // Check title is rendered
      expect(
        screen.getByText('statistics.tagAnalytics.title')
      ).toBeInTheDocument()

      // Check tag names are displayed with # prefix
      expect(screen.getByText('#journal')).toBeInTheDocument()
      expect(screen.getByText('#work')).toBeInTheDocument()

      // Check entry counts are displayed
      expect(
        screen.getByText('10 statistics.tagAnalytics.entries')
      ).toBeInTheDocument()
      expect(
        screen.getByText('5 statistics.tagAnalytics.entries')
      ).toBeInTheDocument()

      // Check average words are displayed
      expect(screen.getByText('500')).toBeInTheDocument()
      expect(screen.getByText('300')).toBeInTheDocument()
    })

    it('shows all required fields (name, entry count, avg words, avg mood)', () => {
      const data = createTagAnalytics([
        createTag({
          name: 'complete-tag',
          entryCount: 15,
          averageWords: 750,
          averageMood: 4.2,
        }),
      ])

      render(<TagAnalyticsChart data={data} />)

      // Tag name
      expect(screen.getByText('#complete-tag')).toBeInTheDocument()

      // Entry count
      expect(
        screen.getByText('15 statistics.tagAnalytics.entries')
      ).toBeInTheDocument()

      // Average words
      expect(screen.getByText('750')).toBeInTheDocument()
      expect(
        screen.getByText('statistics.tagAnalytics.avgWords')
      ).toBeInTheDocument()

      // Average mood
      expect(screen.getByText('4.2')).toBeInTheDocument()
      expect(
        screen.getByText('statistics.tagAnalytics.avgMood')
      ).toBeInTheDocument()
    })
  })

  describe('empty states', () => {
    it('displays empty state when no tags exist', () => {
      const data = createTagAnalytics([])

      render(<TagAnalyticsChart data={data} />)

      expect(
        screen.getByText('statistics.tagAnalytics.noTags')
      ).toBeInTheDocument()
    })

    it('displays empty state when data is undefined', () => {
      render(<TagAnalyticsChart data={undefined} />)

      expect(
        screen.getByText('statistics.tagAnalytics.noTags')
      ).toBeInTheDocument()
    })
  })

  describe('tag limiting and sorting', () => {
    it('limits display to top 10 tags sorted by entry count', () => {
      // Create 15 tags with different entry counts
      const tags = Array.from({ length: 15 }, (_, i) =>
        createTag({
          name: `tag-${i + 1}`,
          entryCount: 100 - i * 5, // 100, 95, 90, ... decreasing
        })
      )
      const data = createTagAnalytics(tags, 15)

      render(<TagAnalyticsChart data={data} />)

      // First 10 tags should be visible (sorted by entry count)
      expect(screen.getByText('#tag-1')).toBeInTheDocument()
      expect(screen.getByText('#tag-10')).toBeInTheDocument()

      // Tags 11-15 should not be visible
      expect(screen.queryByText('#tag-11')).not.toBeInTheDocument()
      expect(screen.queryByText('#tag-15')).not.toBeInTheDocument()

      // Total tags footer should be shown
      expect(screen.getByText(/15/)).toBeInTheDocument()
    })

    it('sorts tags by entry count in descending order', () => {
      const tags = [
        createTag({ name: 'low', entryCount: 5 }),
        createTag({ name: 'high', entryCount: 20 }),
        createTag({ name: 'medium', entryCount: 10 }),
      ]
      const data = createTagAnalytics(tags)

      const { container } = render(<TagAnalyticsChart data={data} />)

      // Get all tag names in order
      const tagElements = container.querySelectorAll(
        '[class*="font-bold"][class*="truncate"]'
      )
      const tagNames = Array.from(tagElements).map((el) => el.textContent)

      expect(tagNames).toEqual(['#high', '#medium', '#low'])
    })
  })

  describe('mood handling', () => {
    it('handles missing mood data gracefully (averageMood: null)', () => {
      const data = createTagAnalytics([
        createTag({ name: 'no-mood', entryCount: 5, averageMood: null }),
      ])

      render(<TagAnalyticsChart data={data} />)

      // Tag should still render
      expect(screen.getByText('#no-mood')).toBeInTheDocument()

      // avgMood label should not be present when mood is null
      expect(
        screen.queryByText('statistics.tagAnalytics.avgMood')
      ).not.toBeInTheDocument()
    })

    it('displays mood when available', () => {
      const data = createTagAnalytics([
        createTag({ name: 'with-mood', entryCount: 5, averageMood: 4.5 }),
      ])

      render(<TagAnalyticsChart data={data} />)

      expect(screen.getByText('4.5')).toBeInTheDocument()
      expect(
        screen.getByText('statistics.tagAnalytics.avgMood')
      ).toBeInTheDocument()
    })
  })

  describe('top tag highlighting', () => {
    it('highlights the top tag with accent styling', () => {
      const data = createTagAnalytics([
        createTag({ name: 'top-tag', entryCount: 100 }),
        createTag({ name: 'second-tag', entryCount: 50 }),
      ])

      const { container } = render(<TagAnalyticsChart data={data} />)

      // Find the top tag element
      const topTag = screen.getByText('#top-tag')
      expect(topTag).toHaveClass('text-accent')

      // Second tag should not have accent color
      const secondTag = screen.getByText('#second-tag')
      expect(secondTag).not.toHaveClass('text-accent')
      expect(secondTag).toHaveClass('text-text-main')

      // Check background bar opacity for top tag
      const bars = container.querySelectorAll('[class*="bg-accent"]')
      expect(bars.length).toBeGreaterThan(0)
    })
  })

  describe('footer behavior', () => {
    it('does not show footer when 10 or fewer tags', () => {
      const tags = Array.from({ length: 10 }, (_, i) =>
        createTag({ name: `tag-${i + 1}`, entryCount: 10 - i })
      )
      const data = createTagAnalytics(tags, 10)

      const { container } = render(<TagAnalyticsChart data={data} />)

      // Footer with total tags count should not be present
      const footer = container.querySelector('[class*="border-t-2"]')
      expect(footer).not.toBeInTheDocument()
    })

    it('shows footer with total tags count when more than 10 tags', () => {
      const tags = Array.from({ length: 12 }, (_, i) =>
        createTag({ name: `tag-${i + 1}`, entryCount: 12 - i })
      )
      const data = createTagAnalytics(tags, 12)

      render(<TagAnalyticsChart data={data} />)

      // Footer should show total tags count
      expect(
        screen.getByText('statistics.tagAnalytics.title: 12')
      ).toBeInTheDocument()
    })
  })
})
